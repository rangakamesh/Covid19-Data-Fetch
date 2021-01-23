import datetime
import logging

import azure.functions as func
import Preprocess19 as pp


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    status = pp.fetchFromRepository()
    
    if status==0:
        logging.info('The covid-19 preprocessing ran successfully and the preprocessed objects were fed to the DB at %s', utc_timestamp)
        return
    else:
        logging.info('The covid-19 preprocessing failed. Please refer to Cloud logs for more info at %s', utc_timestamp)
        return


