from capstone import db


def create_site(name, domain):
    return db.Site(name=name, domain=domain, title=name).save()
