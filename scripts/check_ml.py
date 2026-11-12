for mod in ['xgboost', 'shap', 'sklearn']:
    try:
        m = __import__(mod)
        print(f"{mod}: {getattr(m, '__version__', 'installed')}")
    except ImportError:
        print(f"{mod}: NOT installed")
