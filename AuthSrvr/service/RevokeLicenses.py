from flask_apscheduler import APScheduler
from requests.adapters import HTTPAdapter
from flask import Flask

from datetime import datetime

from .models import User, License_Permit, License, DataValidationError

from . import app

class RevokeLicenses:

    __instance = None
    @staticmethod
    def getInstance():
        if RevokeLicenses.__instance == None:
            RevokeLicenses()
        return __instance
    
    def __init__(self):
        if RevokeLicenses.__instance == None:
            self.apsched = APScheduler()
            self.apsched.start()
            self.jobId = "DormantLicense"
            __instance = self
            self.revokeDormantLicenseSchedule()
        else:
            return self.__instance

    def revokeDormantLicenseSchedule(self): 
        self.apsched.add_job(func=self.revokeDormantLicense, seconds=5, id=self.jobId, trigger='interval')

    def revokeDormantLicense(self):
        with app.app_context():
            dormantLicenses = License.find_in_use_and_last_pinged_before_threshold()
            for license in dormantLicenses:
                license.container_id = None
                license.in_use = False
                permit = License_Permit.find_by_uid(license.user_id)
                permit.in_use -= 1
                permit.update()
                license.update()
                app.logger.info(f"Revoked license {license.id} for user : {license.user_id}")                