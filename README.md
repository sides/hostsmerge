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
```-s```, ```--set``` | See: [Setting](#setting).
```-g```, ```--get``` | See: [Getting](#getting).
```-b```, ```--no-backup``` | Don't make any backups.
```-n```, ```--new``` | Replace contents of old hosts file when merging. See also: [Setting](#setting).
```-o```, ```--sort``` | Sort the rules alphabetically by hostname.
```-H```, ```--hostspath``` | Specify manual path to hosts file. Defaults to system default.
```-B```, ```--backup``` | Specify manual folder for backup files. Defaults to ```backup/```.
```-O```, ```--output``` | Specify manual output file. Defaults to the specified ```hostspath```.
```-l```, ```--hostslist``` | See: [Hostslist](#hostslist).

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
When ```--set``` is specified, the arguments are used to set specific rules. Arguments are counted as pairs, i.e. ```hostsmerge.py --set key1 value1 key2 value2 ...```, and keys can be comma separated. Both keys and values can either be a hostname or an ip address. When the number of arguments are odd and not even the last value is interpreted as "null" (remove).

Depending on whether the key is a hostname or ip address and the value a hostname or ip address, different functionality is performed.

Combination | Explanation
------------- | -------------
```hostname ip``` | Makes ```hostname``` resolve to ```ip```.
```ip hostname``` | Makes ```hostname``` resolve to ```ip```. If ```--new``` is specified, all of ```ip```'s resolves are cleared first.
```hostname1 hostname2``` | Makes ```hostname1``` resolve to the same ip address as ```hostname2```. If ```--new``` is specified, ```hostname2``` will then be removed.
```ip1 ip2``` | Moves all of ```ip2```'s resolves to ```ip1```. If ```--new``` is specified, all of ```ip1```'s resolves are cleared first.
```hostname``` | Removes ```hostname```.
```ip``` | Removes all of ```ip```'s resolves.

## Getting
When ``--get`` is specified, the arguments are used to get information about rules.

```hostsmerge.py --get hostname.com``` will show what ```hostname.com``` resolves to.

```hostsmerge.py --get 127.0.0.1``` will show all hostnames that resolve to ```127.0.0.1```
