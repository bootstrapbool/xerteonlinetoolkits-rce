# Xerte Online Toolkits <= 3.15 Remote Code Execution

## Affected Versions

Xerte Online Toolkits <= 3.15

A backported patch has been applied to versions 3.15, 3.14, and 3.13

## CVEs

- CVE-2026-34413 - Missing Authentication for Critical Function
- CVE-2026-34414 - Relative Path Traversal
- CVE-2026-34415 - CWE-184: Incomplete List of Disallowed Inputs

## Description

Xerte Online Toolkits versions 3.15 and earlier suffer from 3 vulnerabilities in the /editor/elfinder/php/connector.php component, which may be chained together by an unauthenticated attacker to achieve Remote Code Execution (RCE).

### CWE-184: Incomplete List of Disallowed Inputs

Because of a mistake in the connector.php file extension filter regex, attackers can chain a path traversal vulnerability present in the same versions of Xerte to move a file with malicious PHP code to the application root with a .php4 extension.

#### Relevant Code Snippet

The `php*` regex only matches the preceding character. Therefore it would match the following "ph", "php", "phppp", etc...

~~~php
array( // hide readmes
    'pattern' => '/(readme\.txt)|\.(html|php|php5|php*|phtml|phar|inc|py|pl|sh)$/i',
    'read'   => false,
~~~


