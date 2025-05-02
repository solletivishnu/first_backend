import os

def labour_license_upload_employer_details(instance, filename):
    return os.path.join('Labour License', 'EmployerDetails', str(instance.license.id), filename)

def labour_license_upload_file(instance,filename):
    return os.path.join('Labour License', 'files', str(instance.license.id), filename)
