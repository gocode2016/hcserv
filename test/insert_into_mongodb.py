from dao.models import *

with open('../dist/tmp.txt') as f:
    st = set()
    s = f.read()
    s = s.split('\n')
    l = []
    for line in s:
        line = line.strip()
        if not line:
            continue
        game_id, expire_time = line.split('\t')
        game_id = int(game_id)
        expire_time = int(expire_time)
        if game_id not in st:
            st.add(game_id)
            l.append({'game_id': game_id, 'expire_time': expire_time})
    print(l[50])
    u = UserInfo()
    u.insert_many(l)
