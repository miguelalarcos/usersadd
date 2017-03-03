import subprocess
from fabric.api import sudo, env, execute, warn_only
from pymongo import MongoClient
from time import sleep
import pwd
from os.path import join

env.password = 'miguel'
env.skip_bad_hosts = True


def adduser(user, password, uid):
    return sudo('useradd -s /bin/bash {user} -d /mnt/users/{user} -p `openssl passwd {password}` -u {uid}'.
             format(user=user, password=password, uid=uid))


def delete_pending(_id):
    client = MongoClient()
    db = client.academia
    pending = db.pending
    pending.delete_one({'_id': _id})
    client.close()


def get_pendings():
    ret = []
    client = MongoClient()
    db = client.academia
    pending = db.pending
    for p in pending.find():
        ret.append(p)
    client.close()
    return ret
    #return [{'_id':'0', 'host': 'miguel@192.168.1.21', 'user': 'reque8', 'password': 'reque'}]


def main():
    while True:
        for item in get_pendings():
            try:
                uid = pwd.getpwnam(item['user']).pw_uid
            except:
                subprocess.call(['useradd', item['user']])
                home = join('/home', item['user'])
                uid = pwd.getpwnam(item['user']).pw_uid
                subprocess.call(['mkdir', home])
                subprocess.call(['cp', '-rT', join('/etc', 'skel'), home])
                subprocess.call(['chown', '-R', '{user}:{user}'.format(user=item['user']), home])
                subprocess.call(['chmod', '700', home])
            with warn_only():
                result = execute(adduser, hosts=[item['host']], user=item['user'],
                                 password=item['password'], uid=uid)
                host, ret = result.popitem()
                if ret == '':
                    delete_pending(item['_id'])

        sleep(300)
main()
