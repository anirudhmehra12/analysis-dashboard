"""tests for get_data.py"""
from get_data import get_all_users, get_all_site_groups, add_site_to_site_group
from pvsite_datamodel.sqlmodels import UserSQL, SiteGroupSQL, SiteSQL
from pvsite_datamodel.read import get_all_sites
from pvsite_datamodel.write.user_and_site import make_site_group, make_site


# get all users
def test_get_all_users(db_session):
    users = get_all_users(session=db_session)
    # assert
    assert len(users) == 0


# get all sites
def test_get_all_sites(db_session):
    sites = get_all_sites(session=db_session)
    # assert
    assert len(sites) == 0


# get all site groups
def test_get_all_site_groups(db_session):
    site_groups = get_all_site_groups(session=db_session)
    # assert
    assert len(site_groups) == 0


# add site to site group
def test_add_site_to_site_group(db_session):
    site_group = make_site_group(db_session=db_session)
    site_1 = make_site(db_session=db_session, ml_id=1)
    site_2 = make_site(db_session=db_session, ml_id=2)
    site_3 = make_site(db_session=db_session, ml_id=3)
    site_group.sites.append(site_1)
    site_group.sites.append(site_2)

    add_site_to_site_group(
        session=db_session,
        site_uuid=str(site_3.site_uuid),
        site_group_name=site_group.site_group_name,
    )

    assert len(site_group.sites) == 3