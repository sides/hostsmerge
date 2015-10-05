# hostsmerge
Hostsmerge is a command line utility to maintain your system's hosts file.

## Usage
```
hostsmerge.py [options] <file|url> [file|url ...]
hostsmerge.py --set [options] <hostname|ip[,hostname|ip ...]> [hostname|ip] ...
hostsmerge.py --get [options] <hostname|ip> [hostname|ip ...]
```
Will parse options and retrieve contents of specified files and merge them with your hosts file or set/get specific rules.

## Options
Option  | Explanation
------------- | -------------
```-h```, ```--help```  | Show help.
```-v```, ```--version```  | Show version.
```-s```, ```--set``` | See: [Setting](#Setting).
```-g```, ```--get``` | See: [Getting](#Getting).
```-b```, ```--no-backup``` | Don't make any backups.
```-n```, ```--new``` | Replace contents of old hosts file when merging. See also: [Setting](#Setting).
```-o```, ```--sort``` | Sort the rules alphabetically by hostname.
```-H```, ```--hostspath``` | Specify manual path to hosts file. Defaults to system default.
```-B```, ```--backup``` | Specify manual folder for backup files. Defaults to ```backup/```.
```-O```, ```--output``` | Specify manual output file. Defaults to the specified ```hostspath```.
```-l```, ```--hostslist``` | See: [Hostslist](#Hostslist)

## Configuration
Place a ```hostsmerge.conf``` file in the folder where ```hostsmerge.py``` resides and each line will be parsed as an option when running hostsmerge. Example:
```
new
--sort
backup=~/hostsmergebackups/
```
Hyphens are optional and shorthands (```n```, ```o```, ```B```) can be used as well.

## Merging
By default, when neither ```--set``` nor ```--get``` are specified, hostsmerge will merge your hosts file with the sources of the passed arguments, and, if supplied, each line of ```--hostlist```'s contents is accounted as an additional argument. Multiple lists can be passed by separating them by comma.

### Hostslist
Hostslist is a file or URL that contains one source per line. Example:
```
http://someonewhocares.org/hosts/hosts
http://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts&showintro=1&mimetype=plaintext
```

## Setting
When ```--set``` is specified, the arguments are used to set specific rules. Arguments are counted as pairs, i.e. ```hostsmerge.py --set key1 value1 key2 value2 ...```, and keys can be comma separated. If there's no value (when the number of arguments are odd not even) then the last value is interpreted as "null" (remove).

```hostsmerge.py --set badhostname.com 127.0.0.1``` will add the rule ```127.0.0.1  badhostname.com```

```hostsmerge.py --set badhostname.com,worsehostname.com 127.0.0.1``` will add the rules ```127.0.0.1 badhostname.com``` and ```127.0.0.1 worsehostname.com```

```hostsmerge.py --set 127.0.0.1 badhostname``` will add the rule ```127.0.0.1  badhostname.com```

```hostsmerge.py --set --new 127.0.0.1 localhost``` will add the rule ```127.0.0.1  localhost``` and remove all other rules using the same ip address.

```hostsmerge.py --set 127.0.0.1 0.0.0.0``` will move all of ```0.0.0.0```'s rules to ```127.0.0.1```

```hostsmerge.py --set --new 127.0.0.1 0.0.0.0``` will clear all of ```127.0.0.1``` rules and move all of ```0.0.0.0``` rules to ```127.0.0.1```

```hostsmerge.py --set badhostname.com worsehostname.com``` will resolve ```badhostname.com``` to the same ip address as ```worsehostname.com```

```hostsmerge.py --set --new badhostname.com worsehostname.com``` will resolve ```badhostname.com``` to the same ip address as ```worsehostname.com``` and remove ```worsehostname.com```'s rule.

```hostsmerge.py --set badhostname.com``` will remove ```badhostname.com```'s rule.

## Getting
When ``--get`` is specified, the arguments are used to get information about rules.

```hostsmerge.py --get hostname.com``` will show what ```hostname.com``` resolves to.

```hostsmerge.py --get 127.0.0.1``` will show all hostnames that resolve to ```127.0.0.1```
