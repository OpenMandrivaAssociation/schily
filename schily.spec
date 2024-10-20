%bcond_with alsa
%bcond_with pulse

%define dashedver %(echo %{version} |sed -e 's,\\.,-,g')

# Build system doesn't generate debugsources (but does generate debuginfo)
%define _empty_manifest_terminate_build 0

Summary:	A collection of command-line utilities originally written by J.Schilling
Name:		schily
Version:	2021.09.18
Release:	3
License:	Various Open Source Licenses (CDDL.Schily, GPL-2.0, LGPL-2.1, BSD)
Group:		Archiving/Cd burning
URL:		https://schilytools.sourceforge.net/
Source0:	https://nav.dl.sourceforge.net/project/schilytools/%{name}-%{dashedver}.tar.bz2
BuildRequires:	recode
BuildRequires:	pkgconfig(libcap)
%if %{with alsa}
BuildRequires:	pkgconfig(alsa)
%endif
%if %{with pulse}
BuildRequires:	pkgconfig(libpulse)
%endif
Conflicts:	man-pages < 4.05-1
%rename schily-tools

%description
The "Schily" Tool Box is a set of tools originally written by Jörg Schilling.

%package -n cdrtools
Summary:	Tools for working with writable CD, DVD and BluRay media
Group:		Archiving/Cd burning
Obsoletes:	cdrkit < 1.1.11-23
Provides:	cdrkit = 1.1.11-23
Obsoletes:	cdrkit-genisoimage < 1.1.11-23
Provides:	cdrkit-genisoimage = 1.1.11-23
Obsoletes:	cdrkit-icedax < 1.1.11-23
Provides:	cdrkit-icedax = 1.1.11-23
Obsoletes:	cdrkit-isotools < 1.1.11-23
Provides:	cdrkit-isotools = 1.1.11-23
Provides:	cdrecord = %{EVRD}
Provides:	cdrecord-dvdhack = 4:2.01.01-1
Provides:	cdrecord = 4:2.01.01-1
Provides:	cdrecord-cdda2wav = %{EVRD}
Provides:	cdrecord-isotools = %{EVRD}
Provides:	genisoimage = %{EVRD}
Provides:	mkisofs = %{EVRD}
Conflicts:	man-pages < 4.05-1

%description -n cdrtools
Cdrtools is a set of command line programs that allows to
record CD/DVD/BluRay media.

The suite includes the following programs:

  cdrecord  A CD/DVD/BD recording program 
  readcd    A program to read CD/DVD/BD media with CD-clone features 
  cdda2wav  The most evolved CD-audio extraction program with paranoia support 
  mkisofs   A program to create hybrid ISO-9660/Joliet/HFS filesystems
            with optional Rock Ridge attributes 
  isodebug  A program to print mkisofs debug information from media 
  isodump   A program to dump ISO-9660 media 
  isoinfo   A program to analyse/verify ISO-9660/Joliet/Rock-Ridge filesystems 
  isovfy    A program to verify the ISO-9660 structures 
  rscsi     A Remote SCSI enabling daemon 

%package -n star
Summary:	An alternative implementation of the tar command
Group:		Archiving/Backup

%description -n star
An alternative implementation of the tar command.

%package -n smake
Summary:	An alternative implementation of the make command
Group:		Development/Tools

%description -n smake
An alternative implementation of the make command

smake is powerful, but not compatible with GNU make (which is used
by just about everything).

%package -n btcflash
Summary:	Flash tool for BTC CD drives
Group:		Development/Tools

%description -n btcflash
Flash tool for BTC CD drives.

%prep
%autosetup -p1 -n %{name}-%{dashedver}
sed -i -e 's,^INS_BASE=.*,INS_BASE=%{_prefix},g' DEFAULTS/*
sed -i -e 's,-noclobber,,' cdrecord/Makefile.dfl

# Get rid of old ISO-8859-1 encoded umlaut characters
find . -name "*.c" -o -name "*.h" -o -name "*README*" -type f |xargs recode ISO-8859-1..UTF-8

# Remove lib*/*_p.mk to skip the compilation of profiled libs
rm -f lib*/*_p.mk

%ifarch %{ix86}
# doesnt work with clang on i586
sed -i -e 's,^DEFCCOM=.*,DEFCCOM=gcc,g' DEFAULTS/*
%endif

# We can specify LINKMODE="dynamic" here, but it just causes
# dynamic linking to libraries not used anywhere outside of
# schily world - so linking them statically is probably better
MAKEPROG=gmake make RUNPATH="" COPTOPT="%{optflags}" LDOPTX="" SCCS_BIN_PRE="" SCCS_HELP_PRE="" CC="%{__cc}" config

%build
# The Makefile system isn't 100% ready for an SMP build -- can't use -j
MAKEPROG=gmake make RUNPATH="" COPTOPT="%{optflags}" LDOPTX="" SCCS_BIN_PRE="" SCCS_HELP_PRE="" all

%install
MAKEPROG=gmake make RUNPATH="" COPTOPT="%{optflags}" LDOPTX="" SCCS_BIN_PRE="" SCCS_HELP_PRE="" DESTDIR="%{buildroot}" INS_BASE="%{_prefix}" install

# We don't need any Solaris-isms in our filesystem...
# Kill dupes
rm %{buildroot}%{_prefix}/xpg4/bin/{make,sh,od}
# And move the rest to a more reasonable place
mv %{buildroot}%{_prefix}/xpg4/bin/* %{buildroot}%{_prefix}/ccs/bin/* %{buildroot}%{_bindir}
rmdir %{buildroot}%{_prefix}/xpg4/bin %{buildroot}%{_prefix}/ccs/bin
rmdir %{buildroot}%{_prefix}/xpg4 %{buildroot}%{_prefix}/ccs

[ -d %{buildroot}%{_prefix}/sbin ] && mv %{buildroot}%{_prefix}/sbin/* %{buildroot}%{_bindir} && rm -rf %{buildroot}%{_prefix}/sbin

%if "%{_lib}" != "lib"
mkdir -p %{buildroot}%{_libdir}
mv %{buildroot}%{_prefix}/lib/*.so* %{buildroot}%{_libdir}
%endif

# Not much of a point in shipping static libs and headers for libs used
# only by cdrtools
rm -rf \
	%{buildroot}%{_prefix}/lib/*.a \
	%{buildroot}%{_includedir}

# The libraries/headers aren't installed, so we don't need their man
# pages either
rm -rf %{buildroot}%{_mandir}/man3

# Don't conflict with standard tools
# The tools are still available via their s* name
rm -f %{buildroot}%{_bindir}/{make,tar,gnutar,sh} \
	%{buildroot}%{_mandir}/man1/{make,tar,gnutar,sh}.1

%files
%{_bindir}/Cstyle
%{_bindir}/admin
%{_bindir}/bdiff
%{_bindir}/bosh
%{_bindir}/bsh
%{_bindir}/cal
%{_bindir}/calc
%{_bindir}/calltree
%{_bindir}/cdc
%{_bindir}/change
%{_bindir}/comb
%{_bindir}/compare
%{_bindir}/copy
%{_bindir}/count
%{_bindir}/cstyle.js
%{_bindir}/ctags
%{_bindir}/delta
%{_bindir}/devdump
%{_bindir}/diff
%{_bindir}/dmake
%{_bindir}/fdiff
%{_bindir}/fifo
%{_bindir}/fsdiff
%{_bindir}/get
%{_bindir}/hdump
%{_bindir}/help
%{_bindir}/jsh
%{_bindir}/krcpp
%{_bindir}/label
%{_bindir}/lndir
%{_bindir}/man2html
%{_bindir}/match
%{_bindir}/mdigest
%{_bindir}/mt
%{_bindir}/obosh
%{_bindir}/od
%{_bindir}/opatch
%{_bindir}/p
%{_bindir}/pbosh
%{_bindir}/pfbsh
%{_bindir}/pfsh
%{_bindir}/printf
%{_bindir}/prs
%{_bindir}/prt
%{_bindir}/pxupgrade
%{_bindir}/rcs2sccs
%{_bindir}/rmchg
%{_bindir}/rmdel
%{_bindir}/sact
%{_bindir}/sccs
%{_bindir}/sccscvt
%{_bindir}/sccsdiff
%{_bindir}/sccslog
%{_bindir}/sccspatch
%{_bindir}/scgcheck
%{_bindir}/scgskeleton
%{_bindir}/scut
%{_bindir}/sdd
%{_bindir}/sfind
%{_bindir}/sformat
%{_bindir}/sgrow
%{_bindir}/smt
%{_bindir}/spaste
%{_bindir}/spatch
%{_bindir}/spax
%{_bindir}/svr4.make
%{_bindir}/tartest
%{_bindir}/termcap
%{_bindir}/translit
%{_bindir}/udiff
%{_bindir}/unget
%{_bindir}/ustar
%{_bindir}/val
%{_bindir}/vc
%{_bindir}/vctags
%{_bindir}/ved
%{_bindir}/ved-e
%{_bindir}/ved-w
%{_bindir}/what
%{_prefix}/etc/termcap
%{_prefix}/lib/cpp
%{_prefix}/lib/diffh
%{_prefix}/lib/help/locale/C/ad
%{_prefix}/lib/help/locale/C/bd
%{_prefix}/lib/help/locale/C/cb
%{_prefix}/lib/help/locale/C/cm
%{_prefix}/lib/help/locale/C/cmds
%{_prefix}/lib/help/locale/C/co
%{_prefix}/lib/help/locale/C/de
%{_prefix}/lib/help/locale/C/default
%{_prefix}/lib/help/locale/C/ge
%{_prefix}/lib/help/locale/C/he
%{_prefix}/lib/help/locale/C/pr
%{_prefix}/lib/help/locale/C/prs
%{_prefix}/lib/help/locale/C/rc
%{_prefix}/lib/help/locale/C/sc
%{_prefix}/lib/help/locale/C/un
%{_prefix}/lib/help/locale/C/ut
%{_prefix}/lib/help/locale/C/va
%{_prefix}/lib/help/locale/C/vc
%{_prefix}/lib/svr4.make
%doc %{_docdir}/bosh
%doc %{_docdir}/bsh
%doc %{_docdir}/ved
%doc %{_mandir}/de/man1/sdd.1*
%doc %{_mandir}/help/ved.help
%doc %{_mandir}/man1/admin.1*
%doc %{_mandir}/man1/bdiff.1*
%doc %{_mandir}/man1/bosh.1*
%doc %{_mandir}/man1/bsh.1*
%doc %{_mandir}/man1/cal.1*
%doc %{_mandir}/man1/calc.1*
%doc %{_mandir}/man1/calltree.1*
%doc %{_mandir}/man1/cdc.1*
%doc %{_mandir}/man1/change.1*
%doc %{_mandir}/man1/comb.1*
%doc %{_mandir}/man1/compare.1*
%doc %{_mandir}/man1/copy.1*
%doc %{_mandir}/man1/count.1*
%doc %{_mandir}/man1/cstyle.1*
%doc %{_mandir}/man1/delta.1*
%doc %{_mandir}/man1/diff.1*
%doc %{_mandir}/man1/dmake.1*
%doc %{_mandir}/man1/fdiff.1*
%doc %{_mandir}/man1/fifo.1*
%doc %{_mandir}/man1/fsdiff.1*
%doc %{_mandir}/man1/get.1*
%doc %{_mandir}/man1/hdump.1*
%doc %{_mandir}/man1/help.1*
%doc %{_mandir}/man1/jsh.1*
%doc %{_mandir}/man1/krcpp.1*
%doc %{_mandir}/man1/label.1*
%doc %{_mandir}/man1/lndir.1*
%doc %{_mandir}/man1/man2html.1*
%doc %{_mandir}/man1/match.1*
%doc %{_mandir}/man1/mdigest.1*
%doc %{_mandir}/man1/mt.1*
%doc %{_mandir}/man1/obosh.1*
%doc %{_mandir}/man1/od.1*
%doc %{_mandir}/man1/opatch.1*
%doc %{_mandir}/man1/p.1*
%doc %{_mandir}/man1/patch.1*
%doc %{_mandir}/man1/pbosh.1*
%doc %{_mandir}/man1/pfbsh.1*
%doc %{_mandir}/man1/pfsh.1*
%doc %{_mandir}/man1/printf.1*
%doc %{_mandir}/man1/prs.1*
%doc %{_mandir}/man1/prt.1*
%doc %{_mandir}/man1/pxupgrade.1*
%doc %{_mandir}/man1/rcs2sccs.1*
%doc %{_mandir}/man1/readcd.1*
%doc %{_mandir}/man1/rmdel.1*
%doc %{_mandir}/man1/sact.1*
%doc %{_mandir}/man1/sccs-add.1*
%doc %{_mandir}/man1/sccs-admin.1*
%doc %{_mandir}/man1/sccs-branch.1*
%doc %{_mandir}/man1/sccs-cdc.1*
%doc %{_mandir}/man1/sccs-check.1*
%doc %{_mandir}/man1/sccs-clean.1*
%doc %{_mandir}/man1/sccs-comb.1*
%doc %{_mandir}/man1/sccs-commit.1*
%doc %{_mandir}/man1/sccs-create.1*
%doc %{_mandir}/man1/sccs-cvt.1*
%doc %{_mandir}/man1/sccs-deledit.1*
%doc %{_mandir}/man1/sccs-delget.1*
%doc %{_mandir}/man1/sccs-delta.1*
%doc %{_mandir}/man1/sccs-diffs.1*
%doc %{_mandir}/man1/sccs-edit.1*
%doc %{_mandir}/man1/sccs-editor.1*
%doc %{_mandir}/man1/sccs-enter.1*
%doc %{_mandir}/man1/sccs-fix.1*
%doc %{_mandir}/man1/sccs-get.1*
%doc %{_mandir}/man1/sccs-help.1*
%doc %{_mandir}/man1/sccs-histfile.1*
%doc %{_mandir}/man1/sccs-info.1*
%doc %{_mandir}/man1/sccs-init.1*
%doc %{_mandir}/man1/sccs-istext.1*
%doc %{_mandir}/man1/sccs-ldiffs.1*
%doc %{_mandir}/man1/sccs-log.1*
%doc %{_mandir}/man1/sccs-print.1*
%doc %{_mandir}/man1/sccs-prs.1*
%doc %{_mandir}/man1/sccs-prt.1*
%doc %{_mandir}/man1/sccs-rcs2sccs.1*
%doc %{_mandir}/man1/sccs-remove.1*
%doc %{_mandir}/man1/sccs-rename.1*
%doc %{_mandir}/man1/sccs-rmdel.1*
%doc %{_mandir}/man1/sccs-root.1*
%doc %{_mandir}/man1/sccs-sact.1*
%doc %{_mandir}/man1/sccs-sccsdiff.1*
%doc %{_mandir}/man1/sccs-status.1*
%doc %{_mandir}/man1/sccs-tell.1*
%doc %{_mandir}/man1/sccs-unedit.1*
%doc %{_mandir}/man1/sccs-unget.1*
%doc %{_mandir}/man1/sccs-val.1*
%doc %{_mandir}/man1/sccs.1*
%doc %{_mandir}/man1/sccscvt.1*
%doc %{_mandir}/man1/sccsdiff.1*
%doc %{_mandir}/man1/sccslog.1*
%doc %{_mandir}/man1/sccspatch.1*
%doc %{_mandir}/man1/scgcheck.1*
%doc %{_mandir}/man1/scgskeleton.1*
%doc %{_mandir}/man1/scut.1*
%doc %{_mandir}/man1/sdd.1*
%doc %{_mandir}/man1/sfind.1*
%doc %{_mandir}/man1/sgrow.1*
%doc %{_mandir}/man1/smt.1*
%doc %{_mandir}/man1/spaste.1*
%doc %{_mandir}/man1/spatch.1*
%doc %{_mandir}/man1/spax.1*
%doc %{_mandir}/man1/sysV-make.1*
%doc %{_mandir}/man1/tartest.1*
%doc %{_mandir}/man1/termcap.1*
%doc %{_mandir}/man1/translit.1*
%doc %{_mandir}/man1/udiff.1*
%doc %{_mandir}/man1/unget.1*
%doc %{_mandir}/man1/ustar.1*
%doc %{_mandir}/man1/val.1*
%doc %{_mandir}/man1/vc.1*
%doc %{_mandir}/man1/vctags.1*
%doc %{_mandir}/man1/ved-e.1*
%doc %{_mandir}/man1/ved-w.1*
%doc %{_mandir}/man1/ved.1*
%doc %{_mandir}/man1/what.1*
%doc %{_mandir}/man5/changeset.5*
%doc %{_mandir}/man5/sccschangeset.5*
%doc %{_mandir}/man5/sccsfile.5*
%doc %{_mandir}/man5/star.5*
%doc %{_mandir}/man5/streamarchive.5*
%doc %{_mandir}/man8/devdump.8*
%doc %{_mandir}/man8/sformat.8*

%files -n cdrtools
%{_sysconfdir}/sformat.dat
%caps(cap_sys_resource,cap_dac_override,cap_sys_admin,cap_sys_nice,cap_net_bind_service,cap_ipc_lock,cap_sys_rawio+ep) %{_bindir}/cdrecord
%caps(cap_dac_override,cap_sys_admin,cap_sys_nice,cap_net_bind_service,cap_sys_rawio+ep) %{_bindir}/cdda2mp3
%caps(cap_dac_override,cap_sys_admin,cap_sys_nice,cap_net_bind_service,cap_sys_rawio+ep) %{_bindir}/cdda2ogg
%caps(cap_dac_override,cap_sys_admin,cap_sys_nice,cap_net_bind_service,cap_sys_rawio+ep) %{_bindir}/cdda2wav
%{_bindir}/isodebug
%{_bindir}/isodump
%{_bindir}/isoinfo
%{_bindir}/isovfy
%caps(cap_dac_override,cap_sys_admin,cap_net_bind_service,cap_sys_rawio+ep) %{_bindir}/readcd
%{_bindir}/mkisofs
%{_bindir}/mkhybrid
%{_sbindir}/mountcd
%{_sbindir}/rscsi
%{_datadir}/lib/siconv
%{_sysconfdir}/default/cdrecord
%{_sysconfdir}/default/rscsi
%doc %{_docdir}/mkisofs
%doc %{_docdir}/libparanoia
%doc %{_docdir}/rscsi
%doc %{_docdir}/cdda2wav
%doc %{_docdir}/cdrecord
%doc %{_mandir}/man1/cdda2mp3.1*
%doc %{_mandir}/man1/cdda2ogg.1*
%doc %{_mandir}/man1/cdda2wav.1*
%doc %{_mandir}/man1/cdrecord.1*
%doc %{_mandir}/man8/isodebug.8*
%doc %{_mandir}/man8/isodump.8*
%doc %{_mandir}/man8/isoinfo.8*
%doc %{_mandir}/man8/isovfy.8*
%doc %{_mandir}/man8/mkhybrid.8*
%doc %{_mandir}/man8/mkisofs.8*
%doc %{_mandir}/man1/mountcd.1*
%doc %{_mandir}/man1/rscsi.1*

%files -n star
%doc %{_docdir}/rmt
%doc %{_docdir}/star
%config(noreplace) %{_sysconfdir}/default/rmt
%config(noreplace) %{_sysconfdir}/default/star
%{_sbindir}/rmt
%{_bindir}/scpio
%{_bindir}/star
%{_bindir}/suntar
%{_bindir}/star_sym
%{_bindir}/strar
%doc %{_mandir}/man1/rmt.1*
%doc %{_mandir}/man1/scpio.1*
%doc %{_mandir}/man1/star.1*
%doc %{_mandir}/man1/suntar.1*
%doc %{_mandir}/man1/star_sym.1*
%doc %{_mandir}/man1/strar.1*

%files -n smake
%{_libdir}/libmakestate.so*
%{_bindir}/smake
%doc %{_mandir}/man1/smake.1*
%doc %{_mandir}/man5/makefiles.5*
%doc %{_mandir}/man5/makerules.5*
%{_datadir}/lib/make
%{_datadir}/lib/smake

%files -n btcflash
%{_bindir}/btcflash
%doc %{_mandir}/man1/btcflash.1*

