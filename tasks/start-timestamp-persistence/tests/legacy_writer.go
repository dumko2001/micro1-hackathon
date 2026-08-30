package main

import (
	"context"
	"os"
	"strconv"

	"github.com/prometheus/common/promslog"
	"github.com/prometheus/prometheus/model/histogram"
	"github.com/prometheus/prometheus/model/labels"
	"github.com/prometheus/prometheus/storage"
	"github.com/prometheus/prometheus/tsdb"
	"github.com/prometheus/prometheus/tsdb/chunkenc"
	"github.com/prometheus/prometheus/tsdb/tsdbutil"
)

const lifecycleSamples = 130

func shapedHistogram(n int64, profile, ordinal int) *histogram.Histogram {
	h := tsdbutil.GenerateTestHistogram(n)
	switch profile {
	case 2:
		h.Schema = 1
		if ordinal == 0 {
			h.CounterResetHint = histogram.UnknownCounterReset
		} else {
			h.CounterResetHint = histogram.NotCounterReset
		}
	default:
		panic("invalid histogram profile")
	}
	return h
}

func shapedFloatHistogram(h *histogram.Histogram) *histogram.FloatHistogram {
	result := h.ToFloat(nil)
	result.Count *= 1.5
	result.ZeroCount *= 1.5
	result.Sum *= 1.5
	for i := range result.PositiveBuckets {
		result.PositiveBuckets[i] *= 1.5
	}
	for i := range result.NegativeBuckets {
		result.NegativeBuckets[i] *= 1.5
	}
	return result
}

func main() {
	if len(os.Args) != 8 {
		panic("invalid arguments")
	}
	dir, metric := os.Args[1], os.Args[2]
	st, err := strconv.ParseInt(os.Args[3], 10, 64)
	if err != nil {
		panic(err)
	}
	base, err := strconv.ParseInt(os.Args[4], 10, 64)
	if err != nil {
		panic(err)
	}
	count, err := strconv.ParseInt(os.Args[5], 10, 64)
	if err != nil {
		panic(err)
	}
	floatMode, err := strconv.ParseBool(os.Args[6])
	if err != nil {
		panic(err)
	}
	profile, err := strconv.Atoi(os.Args[7])
	if err != nil {
		panic(err)
	}

	opts := tsdb.DefaultOptions()
	opts.MinBlockDuration = 100
	opts.MaxBlockDuration = 100
	opts.EnableSTStorage = true
	opts.XOR2EncodingAllowed = true
	opts.FloatChunkEncoding = chunkenc.EncXOR2
	db, err := tsdb.Open(dir, promslog.NewNopLogger(), nil, opts, nil)
	if err != nil {
		panic(err)
	}
	db.DisableCompactions()
	app := db.AppenderV2(context.Background())
	for ordinal := 0; ordinal < lifecycleSamples; ordinal++ {
		h := shapedHistogram(count+int64(ordinal), profile, ordinal)
		var integer = h
		var floating = shapedFloatHistogram(h)
		if floatMode {
			integer = nil
		} else {
			floating = nil
		}
		sampleST := int64(0)
		if ordinal%3 == 0 {
			sampleST = st + int64(ordinal)
		}
		if _, err := app.Append(0, labels.FromStrings("__name__", metric), sampleST, base+int64(ordinal), 0, integer, floating, storage.AppendV2Options{}); err != nil {
			panic(err)
		}
	}
	if err := app.Commit(); err != nil {
		panic(err)
	}
	if err := db.Close(); err != nil {
		panic(err)
	}
	db, err = tsdb.Open(dir, promslog.NewNopLogger(), nil, opts, nil)
	if err != nil {
		panic(err)
	}
	db.DisableCompactions()
	if err := db.CompactHead(tsdb.NewRangeHead(db.Head(), base, base+lifecycleSamples-1)); err != nil {
		panic(err)
	}
	if err := db.Close(); err != nil {
		panic(err)
	}
}
