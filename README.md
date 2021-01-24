Part of the Covid19 Data Serve project.

The project has three phases :

1. Fetching Data from the source, clean and store it - Completed as part of this repository.
2. Serving formatted data using API services         - Completed as part of <a href="https://github.com/rangakamesh/Covid19-Data-Serve" target="_blank">Covid19-Data-Serve</a>.
3. Serving documentations and bootstraped frontend   - Completed as part of <a href="https://github.com/rangakamesh/Covid19-Data-Serve" target="_blank">Covid19-Data-Serve-Docx</a>.

- You can consume the API at <a href="https://covidserve.azurewebsites.net" target="_blank">covidserve.azurewebsites.net</a>.

- For Endpoint documentation and usage requirements please refer to the <a href="https://blue-water-070724a0f.azurestaticapps.net/" target="_blank">documentations site</a>.


The repository is an Azure Funtion deploy it directly to Azure functions and the job runs every day at 7AM GMT.

If you want to just run the python code locally,
1. Install the dependencies from the *requirements.txt*
2. Go to Preprocess19/preprocess.py and edit the MongoDB variable to your Mongo cluster's connection string
3. Run the file and you should be good to go.

Alternately you can use the <a href="https://colab.research.google.com/gist/rangakamesh/15817b5f3108ea6be64b775f18f4f6dc/covid19-data-fetch.ipynb" target="_blank">Jupyter Notebook</a>.
