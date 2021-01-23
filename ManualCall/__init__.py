import logging

import azure.functions as func
import Preprocess19 as pp

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('COVID19 Data processing HTTP trigger function processed a request.')
    status = pp.fetchFromRepository()

    if status==0:
        return func.HttpResponse(f"The covid-19 preprocessing ran successfully and the preprocessed objects were fed to the DB.")
    else:
        return func.HttpResponse(
             "The covid-19 preprocessing failed. Please refer to Cloud logs for more info.",
             status_code=200
        )
