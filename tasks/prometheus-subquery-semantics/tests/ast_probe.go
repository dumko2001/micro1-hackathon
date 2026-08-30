package main

import (
	"fmt"
	"time"

	"github.com/prometheus/prometheus/promql"
	"github.com/prometheus/prometheus/promql/parser"
)

func preprocess(query string) parser.Expr {
	expr, err := parser.ParseExpr(query)
	if err != nil {
		panic(err)
	}
	result, err := promql.PreprocessExpr(
		expr,
		time.UnixMilli(1_700_000_000_000),
		time.UnixMilli(1_700_003_600_000),
		30*time.Second,
	)
	if err != nil {
		panic(err)
	}
	return result
}

func requireSubquery(query string) *parser.SubqueryExpr {
	result := preprocess(query)
	subquery, ok := result.(*parser.SubqueryExpr)
	if !ok {
		panic(fmt.Sprintf("fixed-time subquery was preprocessed as %T", result))
	}
	return subquery
}

func main() {
	for _, query := range []string{
		`foo[10m:6s] @ 10`,
		`foo[10m:5s] offset 1m @ 123`,
		`foo[10m:5s] @ start()`,
		`foo[10m:5s] @ end()`,
	} {
		requireSubquery(query)
	}

	nested := requireSubquery(`sum(foo @ 20)[10m:6s] @ 10`)
	if _, ok := nested.Expr.(*parser.StepInvariantExpr); !ok {
		panic(fmt.Sprintf("invariant expression inside subquery was not preserved as step-invariant: %T", nested.Expr))
	}

	result := preprocess(`quantile_over_time(0.5, foo[2m:30s] @ 120)`)
	if wrapper, ok := result.(*parser.StepInvariantExpr); ok {
		result = wrapper.Expr
	}
	call, ok := result.(*parser.Call)
	if !ok || len(call.Args) != 2 {
		panic(fmt.Sprintf("unexpected preprocessed call shape: %T", result))
	}
	if _, ok := call.Args[1].(*parser.SubqueryExpr); !ok {
		panic(fmt.Sprintf("range-vector function did not receive a direct subquery: %T", call.Args[1]))
	}
}
