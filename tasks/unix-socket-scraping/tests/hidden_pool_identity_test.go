package scrape

import (
	"net/http"
	"testing"
	"time"

	"github.com/prometheus/common/model"
	"github.com/stretchr/testify/require"

	"github.com/prometheus/prometheus/config"
	"github.com/prometheus/prometheus/discovery/targetgroup"
	"github.com/prometheus/prometheus/model/relabel"
	"github.com/prometheus/prometheus/util/teststorage"
)

func sameConnectionPool(left, right *http.Client) bool {
	return left == right || left.Transport == right.Transport
}

func TestMicro1UnixSocketPoolIdentity(t *testing.T) {
	cfg := &config.ScrapeConfig{
		JobName:                    "unix-socket-pool-identity",
		Scheme:                     "http",
		MetricsPath:                "/metrics",
		ScrapeInterval:             model.Duration(time.Hour),
		ScrapeTimeout:              model.Duration(time.Second),
		MetricNameValidationScheme: model.UTF8Validation,
		RelabelConfigs: []*relabel.Config{
			{
				Action:               relabel.Replace,
				SourceLabels:         model.LabelNames{"__meta_unix_socket"},
				Regex:                relabel.MustNewRegexp("(.*)"),
				TargetLabel:          "__unix_socket__",
				Replacement:          "$1",
				NameValidationScheme: model.UTF8Validation,
			},
			{
				Action:               relabel.Replace,
				SourceLabels:         model.LabelNames{"__meta_slot"},
				Regex:                relabel.MustNewRegexp("(.*)"),
				TargetLabel:          "target_slot",
				Replacement:          "$1",
				NameValidationScheme: model.UTF8Validation,
			},
		},
	}

	sp, err := newScrapePool(
		cfg,
		teststorage.NewAppendable(),
		nil,
		0,
		nil,
		nil,
		&Options{skipJitterOffsetting: true},
		newTestScrapeMetrics(t),
	)
	require.NoError(t, err)
	t.Cleanup(sp.stop)

	clients := map[string]*http.Client{}
	sp.injectTestNewLoop = func(options scrapeLoopOptions) loop {
		clients[options.target.labels.Get("target_slot")] = options.scraper.(*targetScraper).client
		return noopLoop()
	}
	sp.Sync([]*targetgroup.Group{{Targets: []model.LabelSet{
		{model.AddressLabel: "127.0.0.1:8001", "__meta_unix_socket": "/tmp/shared.sock", "__meta_slot": "shared-a"},
		{model.AddressLabel: "127.0.0.2:8001", "__meta_unix_socket": "/tmp/shared.sock", "__meta_slot": "shared-b"},
		{model.AddressLabel: "127.0.0.1:8001", "__meta_unix_socket": "/tmp/other.sock", "__meta_slot": "other"},
		{model.AddressLabel: "127.0.0.1:8002", "__meta_slot": "tcp"},
	}}})

	require.Len(t, clients, 4)
	require.True(t, sameConnectionPool(clients["shared-a"], clients["shared-b"]), "targets using one socket must share one effective HTTP connection pool")
	require.False(t, sameConnectionPool(clients["shared-a"], clients["other"]), "different sockets must not share an HTTP connection pool")
	require.False(t, sameConnectionPool(clients["shared-a"], clients["tcp"]), "Unix and TCP targets must not share an HTTP connection pool")

	oldShared := clients["shared-a"]
	clients = map[string]*http.Client{}
	reloaded := *cfg
	reloaded.EnableCompression = !cfg.EnableCompression
	require.NoError(t, sp.reload(&reloaded))
	require.Len(t, clients, 4)
	require.True(t, sameConnectionPool(clients["shared-a"], clients["shared-b"]), "reload must preserve per-socket pool identity")
	require.False(t, sameConnectionPool(oldShared, clients["shared-a"]), "reload must replace the old Unix-socket connection pool")
}
