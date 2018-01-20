TABLE_NAMES = {
    'save_trade': {
        'PROD': 'prod_orders',
        'PROD_TEST': 'prod_test_orders',
        'BACKTEST': 'backtest_orders'
    },
    'save_summaries': {
        'PROD': 'prod_market_summaries',
        'PROD_TEST': 'prod_test_market_summaries',
        'BACKTEST': 'fixture_market_summaries',
        'COLLECT_FIXTURES': 'fixture_market_summaries'
    },
    'save_markets': {
        'PROD': 'prod_markets',
        'PROD_TEST': 'prod_test_markets',
        'BACKTEST': 'fixture_markets',
        'COLLECT_FIXTURES': 'fixture_markets'
    },
    'save_currencies': {
        'PROD': 'prod_currencies',
        'PROD_TEST': 'prod_test_currencies',
        'BACKTEST': 'fixture_currencies',
        'COLLECT_FIXTURES': 'fixture_currencies'
    },
    'save_assets': {
        'PROD': 'portfolio_assets',
        'PROD_TEST': 'portfolio_assets',
        'BACKTEST': 'portfolio_assets',
    },
    'save_portfolio_report': {
        'PROD': 'portfolio_report',
        'PROD_TEST': 'portfolio_report',
        'BACKTEST': 'portfolio_report',
    }
}