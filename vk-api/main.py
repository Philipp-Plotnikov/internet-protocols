from urllib.request import urlopen
import json
from time import sleep


ACCESS_TOKEN = 'e24545bde24545bde24545bd5de174de74ee245e24545bd8a6ca94116f7870abe7b858b'
API_VERSION = '5.131'


def request(method: str, query_params: str):
    req = f'https://api.vk.com/method/{method}?{query_params}&v={API_VERSION}&access_token={ACCESS_TOKEN}'
    with urlopen(req) as url:
        res = json.loads(url.read())
    return res


def get_user(user_nickname_or_id: str):
    user = request('users.get', f'user_ids={user_nickname_or_id}')
    if user is not None and 'response' in user and 'error' not in user:
        return user


def print_user_friend_list(friend_list):
    for user_id in friend_list:
        sleep(1)
        user = get_user(user_id)
        if not is_deactivated(user):
            username = get_username(user)
            if 'error' not in user:
                raw_friend_list = get_raw_friend_list(user_id)
                if 'error' in raw_friend_list:
                    friend_count = None
                    friend_error = raw_friend_list['error']
                else:
                    friend_count =raw_friend_list['response']['count']
                print(f"User id: {user_id}")
                print(f"User surname/name: {username}")
                if friend_count is None:
                    print(f"Error code: {friend_error['error_code']}. Error message: {friend_error['error_msg']}")
                else:
                    print(f"He/she has {friend_count} friends")
                print()
            else:
                user_error = user['error']
                print(f"Error code: {user_error['error_code']}. Error message: {user_error['error_msg']}")
                print()


def get_user_information(user, field: str):
    if user is not None and 'response' in user and user['response']:
        return user['response'][0][field]


def get_user_id(user):
    return get_user_information(user, 'id')


def is_deactivated(user):
    if user is not None:
        return 'deactivated' in user['response'][0]
    return True


def get_raw_friend_list(user_id: str, count=5):
    return request(
        'friends.get',
        f'user_id={user_id}&count={count}'
    )


def get_friend_list_information(friends, field):
    return friends['response'][field]


def get_friend_list(raw_friend_list):
    if 'error' in raw_friend_list:
        error = raw_friend_list['error']
        print(f"Error code: {error['error_code']}. Error message: {error['error_msg']}")
        return None
    return get_friend_list_information(raw_friend_list, 'items')


def get_username(user):
    first_name = get_user_information(user, 'first_name')
    last_name = get_user_information(user, 'last_name')
    if first_name is None or last_name is None:
        return None
    return f'{last_name} {first_name}'


def print_album_list(owner_id: int):
    global ACCESS_TOKEN
    raw_album_list = request(f"photos.getAlbums", f'owner_id={owner_id}')
    if 'error' in raw_album_list:
        error = raw_album_list['error']
        print(f"Error code: {error['error_code']}. Error message: {error['error_msg']}")
        return
    print(f'Album count: {raw_album_list['response']['count']}')
    for album in enumerate(raw_album_list['response']['items']):
        print(f'Album name: {album[1]['title']}')
        print(f'Album size: {album[1]['size']}')
        print()


if __name__ == '__main__':
    user_nickname = input("Input user nickname: ")
    user = get_user(user_nickname)
    user_id = get_user_id(user)
    if user is None:
        print("User doesn't exist")
    else:
        print("What would you like to get?")
        print("Input 'friends' if you would like to get friend list of specified user.")
        print("Input 'albums' if you would like to get album list of specified user.")
        user_input = input()
        if user_input == 'friends':
            friend_count = input("Input how many friends you would like to see: ")
            raw_friend_list = get_raw_friend_list(user_id, friend_count)
            friend_list = get_friend_list(raw_friend_list)
            if friend_list is not None:
                print(f"{user_nickname} friends:")
                print()
                print_user_friend_list(friend_list)
        elif user_input == 'albums':
            print(f"{user_nickname} albums:")
            print()
            print_album_list(user_id)
        else:
            print('Wrong input')
