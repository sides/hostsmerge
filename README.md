hostsmerge is a command line utility to maintain your system's hosts file

## Usage
```
hostsmerge.py [options] [file|url ...]
hostsmerge.py --set [options] <hostname|ip[,hostname|ip ...]> ...
hostsmerge.py --get [options] <hostname|ip> ...
```
Will parse options and retrieve contents of specified sources and merge them with your hosts file or set/get specific rules.

## Options
```
--help            Show help.
--version         Show version.
-s, --set         See: Setting.
-g, --get         See: Getting.
-B, --no-backup   Don't make any backups.
-n, --new         Replace contents of old hosts file when merging. See also: Setting.
-o, --sort        Sort the rules alphabetically by hostname.
-H, --hosts-file  Specify manual path to hosts file. Defaults to system default.
-O, --output      Specify manual output file. Defaults to the specified --hosts-file.
-l, --list-file   See: Hostslist.
--backup-dir      Specify manual folder for backup files. Defaults to 'backup/'.
```

## Configuration
Place a `hostsmerge.conf` file in the folder where `hostsmerge.py` resides and each line will be parsed as an option when running hostsmerge. Example:
```
n
--sort
backup-dir=~/hostsmerge/backup/
```
Hyphens are optional and shorthands can be used as well.

## Merging
By default, when neither `--set` nor `--get` are specified, hostsmerge will merge your hosts file with the sources of the passed arguments, and, if supplied, each line of `--hostlist`'s contents is accounted for as an additional argument. Multiple lists can be passed by separating them by comma.

### Hostslist
Hostslist is a file or URL that contains one source per line. Example:
```
http://someonewhocares.org/hosts/hosts
~/hostsmerge/rules.txt
```

## Setting
When `--set` is specified, the arguments are used to set specific rules. Arguments are counted as pairs, i.e. `hostsmerge.py --set key1 value1 key2 value2 ...`, and keys can be comma separated. Both keys and values can either be a hostname or an ip address. When the number of arguments are odd and not even the last value is interpreted as "null" (remove).

Depending on whether the key is a hostname or ip address and the value a hostname or ip address, different actions are performed.

```
hostname ip              Makes hostname resolve to ip.
ip hostname              Makes hostname resolve to ip. If --new is specified, all of ip's 
                         resolves are cleared first.
hostname1 hostname2      Makes hostname1 resolve to the same ip address as hostname2. If --new 
                         is specified, hostname2 will then be removed.
ip1 ip2                  Moves all of ip2's resolves to ip1. If --new is specified, all of ip1's 
                         resolves are cleared first.
hostname                 Removes hostname.
ip                       Removes all of ip's resolves.
```

## Getting
When ``--get`` is specified, hostnames or ip addresses are passed as arguments to get information about their rules.

`hostsmerge.py --get hostname.com` will show what `hostname.com` resolves to.

`hostsmerge.py --get 127.0.0.1` will show all hostnames that resolve to `127.0.0.1`
