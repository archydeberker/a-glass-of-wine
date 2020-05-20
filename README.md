# A Glass of Wine May Help
Track Quebec's wine consumption during the COVID-19 crisis

A webapp which allows you to visualize what wine is being bought at SAQ.

We also provide some province-level graphs of coronavirus cases and deaths, in the style popularized by 
[John Burn-Murdoch](https://twitter.com/jburnmurdoch/status/1245466314665271298) of the Financial Times.

See [this blogpost](https://blog.usejournal.com/a-glass-of-wine-may-help-quebecs-cure-for-coronavirus-blues-648e5f5e2a53?source=search_post---------0)
for a description of the project.

## Running the project
The project is pure Python/HTML, utilising Flask for the backend, Jinja for templating, and Bulma CSS for styling.

Wine consumption data is scraped hourly from SAQ.com and stored on S3. You will therefore need access to the
S3 bucket to run the project locally, unless you make other storage arrangements. 

You are free to setup your own S3 bucket and populate it accordingly; the relevant environmental variables are clearly named in [constants.py](/constants.py).
