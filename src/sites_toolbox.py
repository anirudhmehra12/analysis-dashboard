"""This module contains the sites toolbox for the OCF dashboard"""
import os
import streamlit as st

from pvsite_datamodel.connection import DatabaseConnection
from pvsite_datamodel.read import (
    get_all_sites,
    get_user_by_email,
    get_site_by_uuid,
    get_site_group_by_name,
)
from get_data import (
    get_all_users,
    get_all_site_groups,
    get_site_by_client_site_id,
    add_site_to_site_group,
    update_user_site_group,
)


# get details for one user
def get_user_details(session, email: str):
    """Get the user details from the database"""
    user_details = get_user_by_email(session=session, email=email)
    user_site_group = user_details.site_group.site_group_name
    user_site_count = len(user_details.site_group.sites)
    user_sites = [
        {"site_uuid": str(site.site_uuid), "client_site_id": str(site.client_site_id)}
        for site in user_details.site_group.sites
    ]
    return user_sites, user_site_group, user_site_count


# get details for one site
def get_site_details(session, site_uuid: str):
    """Get the site details for one site"""
    site = get_site_by_uuid(session=session, site_uuid=site_uuid)
    site_details = {
        "site_uuid": str(site.site_uuid),
        "client_site_id": str(site.client_site_id),
        "client_site_name": str(site.client_site_name),
        "site_group_names": [
            site_group.site_group_name for site_group in site.site_groups
        ],
        "latitude": str(site.latitude),
        "longitude": str(site.longitude),
        "DNO": str(site.dno),
        "GSP": str(site.gsp),
        "tilt": str(site.tilt),
        "orientation": str(site.orientation),
        "capacity": (f"{site.capacity_kw} kw"),
        "date_added": (site.created_utc.strftime("%Y-%m-%d")),
    }
    return site_details


# select site by site_uuid or client_site_id
def select_site_id(dbsession, query_method: str):
    """Select site by site_uuid or client_site_id"""
    if query_method == "site_uuid":
        site_uuids = [str(site.site_uuid) for site in get_all_sites(session=dbsession)]
        selected_uuid = st.selectbox("Sites by site_uuid", site_uuids)
    elif query_method == "client_site_id":
        client_site_ids = [
            str(site.client_site_id) for site in get_all_sites(session=dbsession)
        ]
        client_site_id = st.selectbox("Sites by client_site_id", client_site_ids)
        site = get_site_by_client_site_id(
            session=dbsession, client_site_id=client_site_id
        )
        selected_uuid = str(site.site_uuid)
    elif query_method not in ["site_uuid", "client_site_id"]:
        raise ValueError("Please select a valid query_method.")
    return selected_uuid


# get details for one site group
def get_site_group_details(session, site_group_name: str):
    """Get the site group details from the database"""
    site_group_uuid = get_site_group_by_name(
        session=session, site_group_name=site_group_name
    )
    site_group_sites = [
        {"site_uuid": str(site.site_uuid), "client_site_id": str(site.client_site_id)}
        for site in site_group_uuid.sites
    ]
    site_group_users = [user.email for user in site_group_uuid.users]
    return site_group_sites, site_group_users


# update a site's site groups
def update_site_group(session, site_uuid: str, site_group_name: str):
    """Add a site to a site group"""
    site_group = get_site_group_by_name(
        session=session, site_group_name=site_group_name
    )
    site_group_sites = add_site_to_site_group(
        session=session, site_uuid=site_uuid, site_group_name=site_group_name
    )
    site_group_sites = [
        {"site_uuid": str(site.site_uuid), "client_site_id": str(site.client_site_id)}
        for site in site_group.sites
    ]
    site = get_site_by_uuid(session=session, site_uuid=site_uuid)
    site_site_groups = [site_group.site_group_name for site_group in site.site_groups]
    return site_group, site_group_sites, site_site_groups


# change site group for user
def change_user_site_group(session, email: str, site_group_name: str):
    """
    Change user to a specific site group name
    :param session: the database session
    :param email: the email of the user"""
    update_user_site_group(
        session=session, email=email, site_group_name=site_group_name
    )
    user = get_user_by_email(session=session, email=email)
    user_site_group = user.site_group.site_group_name
    user = user.email
    return user, user_site_group


# add all sites to the ocf site group
def add_all_sites_to_ocf_group(session, site_group_name="ocf"):
    """Add all sites to the ocf site group
    :param session: the database session
    :param site_group_name: the name of the site group"""
    all_sites = get_all_sites(session=session)

    ocf_site_group = get_site_group_by_name(
        session=session, site_group_name=site_group_name
    )

    site_uuids = [site.site_uuid for site in ocf_site_group.sites]

    sites_added = []

    for site in all_sites:
        if site.site_uuid not in site_uuids:
            ocf_site_group.sites.append(site)
            sites_added.append(str(site.site_uuid))
            session.commit()
            message = f"Added {len(sites_added)} sites to group {site_group_name}."

    if len(sites_added) == 0:
        message = f"There are no new sites to be added to {site_group_name}."

    return message, sites_added


# sites toolbox page
def sites_toolbox_page():
    st.markdown(
        f'<h1 style="color:#FFD053;font-size:48px;">{"OCF Dashboard"}</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<h1 style="color:#63BCAF;font-size:48px;">{"Sites Toolbox"}</h1>',
        unsafe_allow_html=True,
    )

    url = os.environ["SITES_DB_URL"]

    connection = DatabaseConnection(
        url=url,
        echo=True,
    )
    with connection.get_session() as session:
        # get the user details
        users = get_all_users(session=session)
        user_list = [user.email for user in users]
        site_groups = get_all_site_groups(session=session)
        site_groups = [site_group.site_group_name for site_group in site_groups]
        site_uuids = get_all_sites(session=session)
        site_uuid_list = [site.site_uuid for site in site_uuids]

    st.markdown(
        f'<h1 style="color:#63BCAF;font-size:32px;">{"Get User Details"}</h1>',
        unsafe_allow_html=True,
    )
    email = st.selectbox("Enter email of user you want to know about.", user_list)
    # getting user details
    if st.button("Get user details"):
        user_sites, user_site_group, user_site_count = get_user_details(
            session=session, email=email
        )
        st.write(
            "This user is part of the",
            user_site_group,
            "site group, which contains",
            user_site_count,
            "sites.",
        )
        st.write(
            "Here are the site_uuids and client_site_ids for this group:", user_sites
        )
        if st.button("Close user details"):
            st.empty()

    # getting site details
    st.markdown(
        f'<h1 style="color:#63BCAF;font-size:32px;">{"Get Site Details"}</h1>',
        unsafe_allow_html=True,
    )
    query_method = st.radio("Select site by", ("site_uuid", "client_site_id"))

    site_id = select_site_id(dbsession=session, query_method=query_method)

    if st.button("Get site details"):
        site_details = get_site_details(session=session, site_uuid=site_id)
        site_id = (
            site_details["client_site_id"]
            if query_method == "client_site_id"
            else site_details["site_uuid"]
        )
        st.write("Here are the site details for site", site_id, ":", site_details)
        if st.button("Close site details"):
            st.empty()

    # getting site group details
    st.markdown(
        f'<h1 style="color:#63BCAF;font-size:32px;">{"Get Site Group Details"}</h1>',
        unsafe_allow_html=True,
    )
    site_group_name = st.selectbox("Enter the site group name.", site_groups)
    if st.button("Get site group details"):
        site_group_sites, site_group_users = get_site_group_details(
            session=session, site_group_name=site_group_name
        )
        st.write(
            "Site group",
            site_group_name,
            "contains the following",
            len(site_group_sites),
            "sites:",
            site_group_sites,
        )
        st.write(
            "The following",
            len(site_group_users),
            "users are part of this group:",
            site_group_users,
        )
        if st.button("Close site group details"):
            st.empty()
        # add site to site group
    st.markdown(
        f'<h1 style="color:#63BCAF;font-size:32px;">{"Add Site to Site Group"}</h1>',
        unsafe_allow_html=True,
    )
    site_uuid = st.selectbox("Select site", site_uuid_list, key="add")
    site_group = st.selectbox("Select site group", site_groups)
    if st.button("Add site to site group"):
        site_group, site_group_sites, site_site_groups = update_site_group(
            session=session, site_uuid=site_uuid, site_group_name=site_group
        )
        st.write(
            "Site",
            site_uuid,
            "has been added to",
            site_group.site_group_name,
            ", which has",
            len(site_group_sites),
            "sites: ",
            site_group_sites,
        )
        st.write(
            "The following site groups include site", site_uuid, ":", site_site_groups
        )
        if st.button("Close details"):
            st.empty()

    # getting site group details
    st.markdown(
        f'<h1 style="color:#63BCAF;font-size:32px;">{"Add All Sites to OCF Group"}</h1>',
        unsafe_allow_html=True,
    )
    if st.button("Add Sites to OCF group"):
        message = add_all_sites_to_ocf_group(session=session, site_group_name="ocf")
        st.write(message)
        if st.button("Close details"):
            st.empty()

    # update user site group
    st.markdown(
        f'<h1 style="color:#63BCAF;font-size:32px;">{"Change User Site Group"}</h1>',
        unsafe_allow_html=True,
    )
    email = st.selectbox("Select user whose site group will change.", user_list)
    site_group_name = st.selectbox("Select site group for user", site_groups)

    if st.button("Change user's site group"):
        user, user_site_group = change_user_site_group(
            session=session, email=email, site_group_name=site_group_name
        )
        st.write(user, "is now in the", user_site_group, "site group.")
        if st.button("Close"):
            st.empty()