# Change log

fastapi-bootcamp is versioned with [semver](https://semver.org/).
Dependencies are updated to the latest available version during each release, and aren't noted here.

Find changes for the upcoming release in the project's [changelog.d directory](https://github.com/lsst-sqre/fastapi-bootcamp/tree/main/changelog.d/).

<!-- scriv-insert-here -->

<a id='changelog-1.0.0'></a>
## 1.0.0 (2024-04-30)

### New features

- Add examples of FastAPI path operation functions to the external router.

- Add `/fastapi-bootcamp/astroplan` router with a basic API for observational sites and computing the observability of targets from those sites. This API is build around [astroplan](https://astroplan.readthedocs.io/en/stable/). We're including it in this app to demonstrate the service architecture that we prefer in SQuaRE, where the application's domain is isolated from concerns of the web API and even storage and other types of external adapters.
