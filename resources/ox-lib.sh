#!/bin/bash
#
# Univention Open-Xchange integration
#
# Copyright (C) 2008-2019 Univention GmbH <http://www.univention.de/>
#
# and
#     iKu Systems & Services GmbH & Co. KG
#
# http://www.iku-systems.de/
#
# All rights reserved.
#
# The source code of this program is made available
# under the terms of the GNU Affero General Public License version 3
# (GNU AGPL V3) as published by the Free Software Foundation.
#
# Binary versions of this program provided by Univention to you as
# well as other copyrighted, protected or trademarked materials like
# Logos, graphics, fonts, specific documentations and configurations,
# cryptographic keys etc. are subject to a license agreement between
# you and Univention and not subject to the GNU AGPL V3.
#
# In the case you use this program under the terms of the GNU AGPL V3,
# the program is provided in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License with the Debian GNU/Linux or Univention distribution in file
# /usr/share/common-licenses/AGPL-3; if not, see
# <http://www.gnu.org/licenses/>.
OXSERVER='software.open-xchange.com'

OXPATH="/opt/open-xchange"
OXADMINPATH="$OXPATH/sbin"

OXSECRETPATH="/etc/ox-secrets"
OXMASTERSECRETFILE="$OXSECRETPATH/master.secret"

_ox_lib_main () {
	case "${0##*/}" in
	ox[_-]timezone) ox_timezone ; exit $? ;;
	ox[_-]language) ox_language ; exit $? ;;
	esac
}

die () { # [rv] "text"
	local rv=1
	case "$1" in
	[0-9]*) rv="$1" ; shift ;;
	esac
	msg "$*" >&2
	exit "$rv"
}
msg () {
	: ${_OX_TERM_BOLD=$(tty <&2 >/dev/null && tput bold)}
	: ${_OX_TERM_NORM=$(tty <&2 >/dev/null && tput sgr0)}
	echo "${_OX_TERM_BOLD}${0##*/}:${_OX_TERM_NORM} $*" >&2
}

ox_timezone () {
	local current_timezone="$(ox_get_timezone)"
	ox_translate_timezone "$current_timezone"
}
ox_get_timezone () {
	local current_timezone="UTC"
	if [ -s /etc/timezone ]
	then
		current_timezone="$(cat /etc/timezone)"
	elif [ -L /etc/localtime ]
	then
		current_timezone="$(readlink /etc/localtime)"
		current_timezone="${current_timezone#/usr/share/zoneinfo/}"
	fi
	echo "$current_timezone"
}
ox_translate_timezone () { # "time-zone-name"
	local current_timezone="$1"
	local OXTIMEZONE="UTC"
	local _self="${BASH_SOURCE:-$0}"
	while read timezone substitute
	do
		if [ "$timezone" = "$current_timezone" ]
		then
			OXTIMEZONE="${substitute:-$timezone}"
			break
		fi
	done <"${_self%/*}/timezones.csv"
	echo "$OXTIMEZONE"
}

ox_language () {
	local locale="$(ucr get locale/default)"
	local OXLANG
	case "${locale%%.*}" in
	de*) OXLANG="de_DE" ;;
	*) OXLANG="en_US" ;;
	esac
	echo "$OXLANG"
}

ox_restart () {
	if systemctl list-units | grep -q open-xchange-documentconverter-server && \
	systemctl is-enabled open-xchange-documentconverter-server.service; then
	    echo "Restarting open-xchange-documentconverter-server..."
		deb-systemd-invoke restart open-xchange-documentconverter-server.service
	fi
	echo "Restarting open-xchange (this might take a while)..."
	deb-systemd-invoke restart open-xchange.service
	/usr/sbin/wait_for_ox_server
	if systemctl list-units | grep -q open-xchange-mobile-api-facade && \
	systemctl is-enabled open-xchange-mobile-api-facade.service; then
	    echo "Restarting open-xchange-mobile-api-facade..."
		deb-systemd-invoke restart open-xchange-mobile-api-facade.service
	fi
}

ox_context_check_ldap () { # "contextXX"
	local res OXCONTEXTNAME="$1"
	local OXHOSTNAME="${OXHOSTNAME:-$(hostname -f)}"
	res="$(univention-ldapsearch -LLL -o ldif-wrap=no "(&(objectClass=oxContext)(cn=$OXCONTEXTNAME))" oxHomeServer oxDBServer)" ||
		die 3 "Failed to lookup OX-context '$OXCONTEXTNAME'."
	[ -z "$res" ] &&
		return 0 # does not exist

	declare -a hosts=($(echo "$res" |
		fgrep -x -v -e "oxHomeServer: ${OXHOSTNAME}" -e "oxDBServer: ${OXDB:-$OXHOSTNAME}" |
		sed -rne 's/^(oxHomeServer|oxDBServer): //p' |
		sort -u))
	[ -n "${hosts:-}" ] &&
		[ -n "$(_ox_lookup_fqdn "${hosts[@]}")" ] &&
		_ox_context_conflict_ldap "$OXCONTEXTNAME"

	return 1
}
_ox_lookup_fqdn () {
	local fqdn filter=
	for fqdn in "$@" # work-around Bug #34327
	do
		filter+="(&(cn=${fqdn%%.*})(associatedDomain=${fqdn#*.}))"
	done
	univention-directory-manager computers/computer list ${BINDARGS+"${BINDARGS[@]}"} \
		--filter "(&(service=ox)(|${filter}))" |
		sed -ne 's/^DN: //p'
}
_ox_context_conflict_ldap () {
	local res OXCONTEXTNAME="$1"
	shift || die "Missing argument"
	res="$(univention-directory-manager oxmail/oxcontext list ${BINDARGS+"${BINDARGS[@]}"} \
		--filter name="$OXCONTEXTNAME" |
		sed -rne '/: None$/d;/^DN:|^  /p')"
	exec >&2
	echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
	echo "The context '$OXCONTEXTNAME' is currently registered as:"
	echo "$res"
	echo
	echo "The referenced host is still registered for the service 'ox'."
	echo "If you're sure the context is no longer used like this, remove the"
	echo "context or update the context to point to this host."
	echo "This can be done through the UMC or on the command line using"
	echo
	echo "  univention-directory-manager oxmail/oxcontext remove \\"
	ox_print_bind '    %s \\\n'
	echo "    --dn 'cn=$OXCONTEXTNAME,cn=open-xchange,$ldap_base'"
	echo "or"
	echo "  univention-directory-manager oxmail/oxcontext modify \\"
	ox_print_bind '    %s \\\n'
	echo "    --dn 'cn=$OXCONTEXTNAME,cn=open-xchange,$ldap_base' \\"
	echo "    --set hostname='${OXHOSTNAME}' \\"
	echo "    --set oxDBServer='${OXDB:-$OXHOSTNAME}'"
	echo
	echo "After that re-run the join script through UMC or on the command line using"
	echo
	echo "  univention-run-join-scripts"
	echo "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
	die "Aborting now."
}
ox_print_bind () {
	local format="${1:- %s}"
	set -- ${BINDARGS+"${BINDARGS[@]}"}
	while [ $# -ge 1 ]
	do
		case "$1" in
		--binddn|--bindpwdfile) printf "$format" "$1 '$2'" ; shift 2 || : ;;
		--bindpwd|--bindpw) printf "$format" "$1 '${2//?/X}'" ; shift 2 || : ;;
		*) shift ;;
		esac
	done
}

ox_write_secret () { # "/etc/FILE.secret" "password"
	local filename="$1" secret="${2:-}"
	mkdir -p "${filename%/*}"
	touch "$filename"
	chmod 0600 "$filename"
	chown 0:0 "$filename"
	[ -n "$secret" ] && echo "$secret" >"$filename"
}

ox_cleanup_old_components () {
	local IFS regexp pattern prefix="^repository/online/component/"
	IFS='|'
	pattern="(($*)[0-9]*)"
	regexp="${prefix}${pattern}/server"
	IFS=$'\n'
	set -- $(ucr search --brief --non-empty --key "${regexp}\$" | sed -rne "s,${regexp}: (https?://(.+:.+@)?)?${OXSERVER}$,\1,p") # IFS
	[ $# -ge 1 ] || return
	IFS='|'
	pattern="($*)"
	regexp="${prefix}${pattern}"
	ucr --keys-only search --brief --non-empty --key "${regexp}" |
		xargs -r -d '\n' ucr unset
	ox_components_available="$(printf '%s' "$ox_components_available" | tr , '\n' | egrep -v -x "$pattern" | tr '\n' ,)"
}

check_credentials () {
	local username password

	username="$(ucr get ox/ldbaccount/username)"
	ldbpasswordfile=$(ucr get ox/ldbaccount/passwordfile)
	if ! [[ -e "$ldbpasswordfile" ]]; then
		echo "Missing passwordfile $ldbpasswordfile for OX repositories."
		password=""
	else
		password="$(cat -- "$ldbpasswordfile")"
	fi

	if [[ -n "$username" ]] && [[ -n "$password" ]]
	then
		echo "Username and password for OX repositories were given."
		return 0
	else
		echo "No username or password for OX repositories given."
		return 1
	fi
}

test_ox_repo_auth () {
	local username password testpath res

	username="$(ucr get ox/ldbaccount/username)"
	ldbpasswordfile=$(ucr get ox/ldbaccount/passwordfile)
	password="$(cat -- "$ldbpasswordfile")"
	testpath="/OX6/OXSEforUCS/4.4/maintained/component/backend7102/"

	if res="$(wget -v "https://${username}:${password}@${OXSERVER}${testpath}" -O /dev/null 2>&1)"; then
		echo "Success connecting to OX repository server."
		return 0
	else
		echo "Error connecting to OX repository server:"
		echo "$res"
		echo "---"
		return 1
	fi
}

ox_setup_components () {
	local comp ldbusername ldbpassword IFS='='

	if ! check_credentials || ! test_ox_repo_auth; then
		return
	fi

	ldbusername=$(ucr get ox/ldbaccount/username)
	ldbpasswordfile=$(ucr get ox/ldbaccount/passwordfile)
	ldbpassword="$(cat -- "$ldbpasswordfile")"

	declare -a ucr=()
	ucr+=(
		"repository/credentials/OpenXchange Update Services/username?${ldbusername}"
		"repository/credentials/OpenXchange Update Services/password?${ldbpassword}"
		"repository/credentials/OpenXchange Update Services/uris?${OXSERVER}"
	)
	for comp in "$@"
	do
		set -- ${comp} # IFS
		ucr+=(
			"repository/online/component/$1=enabled"
			"repository/online/component/$1/server?https://${OXSERVER}"
			"repository/online/component/$1/prefix?OX6/OXSEforUCS"
			"repository/online/component/$1/username?${ldbusername}"
			"repository/online/component/$1/password?${ldbpassword}"
			"repository/online/component/$1/description?$2"
			${3:+"repository/online/component/$1/defaultpackage=$3"}
		)
		ox_components_available="${ox_components_available:+${ox_components_available},}${1}"
	done
	ucr+=(ox/components/available="${ox_components_available#,}")
	ucr set "${ucr[@]}"
}

ox_retry () {
	local rv=2 max=300 step=5 rem stderr
	stderr=$(mktemp)
	for ((rem=max;rem>0;rem+=-step))
	do
		rv=0
		"$@" 2> >(exec tee "$stderr") && break
		rv=$?
		egrep -q 'please try again later|Database is locked or is now beeing updated|Categories=TRY_AGAIN|Connection refused|Verbindungsaufbau abgelehnt|OXContext_V2|OXUser_V2|OXDomain_V2' "$stderr" || break
		printf "%d " "$rem" >&2
		sleep "$step"
	done
	rm -f "$stderr"
	return $rv
}

setup_vars () {
	OXADMINMASTER="oxadminmaster"
	OXADMINMASTERPW="$(cat "$OXMASTERSECRETFILE")"

	OXHOSTNAME="$hostname.$domainname"
	test -n "$OXIMAPSERVER" || OXIMAPSERVER="$OXHOSTNAME"
	OXTIMEZONE="$(ox_timezone)"
	OXLANG="$(ox_language)"

	local OXFILESTORE="/var/oxfilestore"
	OXFILESTORESIZE=$(($(stat -c '%a*%S/1024/1126' -f "$OXFILESTORE")))

	if [ "$OXCONTEXTNAME" = "context10" ]; then
		CONTEXTADMIN="oxadmin"
	else
		CONTEXTADMIN="oxadmin-$OXCONTEXTNAME"
	fi
	CONTEXTDOMAIN="$domainname"
	CONTEXTADMINMAIL="$CONTEXTADMIN@$CONTEXTDOMAIN"
}

prepare_oxadmin_secret () {
	CONTEXTSECRETFILE="$OXSECRETPATH/context${CONTEXTNUM}.secret"
	if [ -f "$CONTEXTSECRETFILE" ]
	then
		msg "Re-using context administrator '$CONTEXTADMIN' credentials..."
		CONTEXTADMINPW="$(cat "$CONTEXTSECRETFILE")" ||
			die "Failed to read secret from '$CONTEXTSECRETFILE'."
	else
		if [ -z "$CONTEXTADMINPW" ];
		then
			msg "Creating context administrator '$CONTEXTADMIN' credentials..."
			CONTEXTADMINPW="$("$OXPATH/sbin/genpw.sh")"
		else
			msg "Using supplied context administrator '$CONTEXTADMIN' credentials..."
		fi
		ox_write_secret "$CONTEXTSECRETFILE" "$CONTEXTADMINPW" ||
			die "Failed to save secret in '$CONTEXTSECRETFILE'."
	fi
}

list_context () {
	/opt/open-xchange/sbin/allpluginsloaded
	ox_retry \
	"$OXADMINPATH/listcontext" \
		--adminuser "$OXADMINMASTER" \
		--adminpass "$OXADMINMASTERPW" \
		--searchpattern "$OXCONTEXTNAME" \
		--csv |
		grep -F -q "$OXCONTEXTNAME"
}

create_context () {
	msg "Creating Open-Xchange context..."
	local max=${1:-600} step=${2:-5} rem
	/opt/open-xchange/sbin/allpluginsloaded
	printf "Trying %d times to create context ..." "$((max/step))" >&2
	for ((rem=max;rem>0;rem+=-step))
	do
		"$OXADMINPATH/createcontext" \
			--adminuser "$OXADMINMASTER" \
			--adminpass "$OXADMINMASTERPW" \
			--contextid "$CONTEXTNUM" \
			--contextname "$OXCONTEXTNAME" \
			--addmapping "$OXCONTEXTNAME" \
			--language "$OXLANG" \
			--timezone "$OXTIMEZONE" \
			--username "$CONTEXTADMIN" \
			--displayname "OX Admin" \
			--givenname "OX" \
			--surname "Admin" \
			--email "$CONTEXTADMINMAIL" \
			--quota "$OXFILESTORESIZE" \
			--password "$CONTEXTADMINPW" >&2 &&
			{ echo >&2 ; return 0 ; }
		sleep "$step"
		list_context &&
			{ echo >&2 ; return 0 ; }
		printf "%d " "$rem" >&2
	done
	die 1 "Failed to create Open-Xchange context."
}

register_oxcontext () {
	msg "Registering Open-Xchange context in LDAP..."
	local OXVERSION
	OXVERSION="$(dpkg-query -W -f '${Version}' univention-ox 2>/dev/null)"
	univention-directory-manager oxmail/oxcontext create ${BINDARGS+"${BINDARGS[@]}"} \
		--position "cn=open-xchange,$ldap_base" \
		--set name="$OXCONTEXTNAME" \
		--set hostname="$OXHOSTNAME" \
		--set contextid="$CONTEXTNUM" \
		--set oxintegrationversion="$OXVERSION" \
		--set oxQuota="$OXFILESTORESIZE" \
		--set oxDBServer="${OXDB:-$OXHOSTNAME}" && return 0
	echo "Failed to create context '$OXCONTEXTNAME' in LDAP." >&2
	ox_context_check_ldap "$OXCONTEXTNAME" &&
		die 2 "Faild to create context '$OXCONTEXTNAME' for unknown reason."
	msg "Updating existing Open-Xchange context in LDAP..."
	univention-directory-manager oxmail/oxcontext modify ${BINDARGS+"${BINDARGS[@]}"} \
		--dn "cn=$OXCONTEXTNAME,cn=open-xchange,$ldap_base" \
		--set hostname="$OXHOSTNAME" \
		--set oxintegrationversion="$OXVERSION" \
		--set oxQuota="$OXFILESTORESIZE" \
		--set oxDBServer="${OXDB:-$OXHOSTNAME}" && return 0
	die 0 "Failed to update context '$OXCONTEXTNAME'."
}

add_ox_permission_flag () {
	# add permission $1 to UCR variable ox/cfg/permissions.properties/permissions
	local permissions="$(ucr get ox/cfg/permissions.properties/permissions)"
	local module="$1"
	if [[ ",${permissions}," == *",${module},"* ]] ; then
		echo "OX permission '$module' already set"
	else
		echo "Adding OX permission '$module'"
		# "${foo:+,}" evaluates to "," if variable foo is non-empty
		ucr set ox/cfg/permissions.properties/permissions="$(echo "${permissions}${permissions:+,}$module" | sed -re 's/^,+//' -e 's/,+$//' -e 's/,+/,/g')"
	fi
}


_ox_lib_main
