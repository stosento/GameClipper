def convert_short_timestamp(time_str):
    global frame_msec
    h,m,s = time_str.split(':')

    h_msec = int(h) * 3600 * 1000
    m_msec = int(m) * 60 * 1000
    s_msec = int(s) * 1000

    total_sec = h_msec + m_msec + s_msec

    return total_sec