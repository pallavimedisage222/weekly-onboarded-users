class Query:

    MEMBERS_DATA = """ select m.fname first_name, m.lname last_name, s.title speciality, m.mobile_number, m.country_code, m.email, \
                        m.country, m.state, m.city, date_format(m.created_at, '%%Y-%%m-%%d') created_at, \
                        if(m.device_token is null, 'App User', 'Web User') user_type from members m \
                        left join specialities s on s.id = m.speciality_id \
                        where m.email not like '%%mymedisage.com%%' and date_format(m.created_at, '%%Y-%%m-%%d') between '{start_date}' and '{end_date}' """

    CURRENT_YEAR_MEMBERS_DATA = """ select m.fname first_name, m.lname last_name, s.title speciality, m.mobile_number, m.country_code, m.email, \
                        m.country, m.state, m.city, date_format(m.created_at, '%%Y-%%m-%%d') created_at, \
                        if(m.device_token is null, 'App User', 'Web User') user_type from members m \
                        left join specialities s on s.id = m.speciality_id \
                        where m.email not like '%%mymedisage.com%%' and date_format(m.created_at, '%%Y') = {current_year} """