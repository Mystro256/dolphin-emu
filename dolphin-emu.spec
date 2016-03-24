%undefine _hardened_build
#Git commit hash for manpages
%global mpcommit 84483a1076710666109bea3b4254b01e9d9f6f6b

Name:           dolphin-emu
Version:        5.0
Release:        0.2rc%{?dist}
Summary:        GameCube / Wii / Triforce Emulator

Url:            http://dolphin-emu.org/
License:        GPLv2 and BSD and Public Domain
Source0:        https://github.com/%{name}/dolphin/archive/5.0-rc.tar.gz
#Grab the current manpages from upstream (will be added for 5.0):
Source1:        https://raw.githubusercontent.com/%{name}/dolphin/mpcommit/Data/%{name}.6
Source2:        https://raw.githubusercontent.com/%{name}/dolphin/mpcommit/Data/%{name}-nogui.6
#GTK3 patch, upstream doesn't care for gtk3
Patch0:         %{name}-%{version}-gtk3.patch
#Patch to enable use of shared gtest
#https://bugs.dolphin-emu.org/issues/9402
Patch1:         %{name}-%{version}-gtest.patch
#Patch for mbedtls instead of polarssl
#Fixed upstream, patch is based on these 3 commits:
#https://github.com/Tilka/dolphin/commit/063446c46ff743d458b43025056bd01988b57ff6
#https://github.com/Tilka/dolphin/commit/f6795466e767ee11e3f2c7d93c8f51abeabd29af
#https://github.com/sepalani/dolphin/commit/5be64d39b0ab463edc286e789d21ebefa62cbaa7
Patch2:         %{name}-%{version}-mbedtls.patch

BuildRequires:  alsa-lib-devel
BuildRequires:  bluez-libs-devel
BuildRequires:  bochs-devel
BuildRequires:  cmake
BuildRequires:  enet-devel
BuildRequires:  gtest-devel
BuildRequires:  gtk3-devel
BuildRequires:  libao-devel
BuildRequires:  libevdev-devel
BuildRequires:  libpng-devel
BuildRequires:  libusb-devel
BuildRequires:  libXrandr-devel
BuildRequires:  lzo-devel
BuildRequires:  mbedtls-devel
BuildRequires:  mesa-libGL-devel
BuildRequires:  miniupnpc-devel
BuildRequires:  openal-soft-devel
BuildRequires:  pulseaudio-libs-devel
BuildRequires:  portaudio-devel
BuildRequires:  SDL2-devel
BuildRequires:  SFML-devel
BuildRequires:  SOIL-devel
BuildRequires:  soundtouch-devel
BuildRequires:  wxGTK3-devel
BuildRequires:  zlib-devel

BuildRequires:  gettext
BuildRequires:  desktop-file-utils

#Only the following architectures are supported:
ExclusiveArch:  x86_64 armv7l aarch64

#xxhash doesn't appear to be in Fedora, will unbundle if it's packaged
#Note that xxhash was unversioned prior to 0.5.0, 0.4.39 is a placeholder
#It was actually called r39: https://github.com/Cyan4973/xxHash/tree/r39
Provides:       bundled(xxhash) = 0.4.39

Requires:       hicolor-icon-theme

#Most of below is taken bundled spec file in source#
%description
Dolphin is a Gamecube, Wii and Triforce (the arcade machine based on the
Gamecube) emulator, which supports full HD video with several enhancements such
as compatibility with all PC controllers, turbo speed, networked multiplayer,
and more.
Most games run perfectly or with minor bugs.

%package nogui
Summary:        Dolphin Emulator without a graphical user interface

%description nogui
Dolphin Emulator without a graphical user interface

####################################################

%prep
%setup -q -n dolphin-%{version}-rc
%patch0 -p1
%patch1 -p1
%patch2 -p1
#Fix an rpmlint warning:
sed -i "/#!/d" Installer/%{name}.desktop

#Allow building with cmake macro
sed -i '/CMAKE_C.*_FLAGS/d' CMakeLists.txt

###Remove Bundled Libraries except xxhash, mentioned above:
cd Externals
rm -rf `ls | grep -v 'Bochs' | grep -v 'xxhash' | grep -v 'GL'`
#Remove Bundled Bochs source and replace with links:
cd Bochs_disasm
rm -rf `ls | grep -v 'stdafx' | grep -v 'CMakeLists.txt'`
ln -s %{_includedir}/bochs/config.h ./config.h
ln -s %{_includedir}/bochs/disasm/* ./

%build
%cmake \
       -DUSE_SHARED_ENET=TRUE \
       -DwxWidgets_CONFIG_EXECUTABLE=%{_libexecdir}/wxGTK3/wx-config \
       .

make %{?_smp_mflags}

%install
make %{?_smp_mflags} install DESTDIR=%{buildroot}

desktop-file-validate %{buildroot}/%{_datadir}/applications/%{name}.desktop

#Install manpages:
install -p -D -m 0644 %{SOURCE1} %{buildroot}/%{_mandir}/man6/%{name}.6
install -p -D -m 0644 %{SOURCE2} %{buildroot}/%{_mandir}/man6/%{name}-nogui.6

%find_lang %{name}

%files -f %{name}.lang
%doc license.txt Readme.md
%{_datadir}/%{name}
%{_bindir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_mandir}/man6/%{name}.*
%{_datadir}/pixmaps/%{name}.xpm

%files nogui
%doc license.txt Readme.md
%{_bindir}/%{name}-nogui
%{_mandir}/man6/%{name}-nogui.*

%post
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%postun
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%changelog
* Thu Mar 24 2016 Jeremy Newton <alexjnewt at hotmail dot com> - 5.0-0.2rc
- Update manpages to upstream
- Disable hardened build (breaks dolphin)

* Thu Mar 3 2016 Jeremy Newton <alexjnewt at hotmail dot com> - 5.0-0.1rc
- Update to 5.0rc
- Updated manpage

* Thu Nov 12 2015 Jeremy Newton <alexjnewt at hotmail dot com> - 4.0-10
- Patch for mbedtls updated for 2.0+ (f23+)

* Thu Nov 12 2015 Jeremy Newton <alexjnewt at hotmail dot com> - 4.0-9
- Patch for X11 for f22+
- Patch for mbedtls (used to be polarssl, fixes check)
- Changed the source download link (migrated to github)

* Mon Jul 20 2015 Jeremy Newton <alexjnewt at hotmail dot com> - 4.0-8
- Disabling polarssl check, as its not working on buildsys

* Sun Jun 14 2015 Jeremy Newton <alexjnewt at hotmail dot com> - 4.0-7
- Patching for the rename of polarssl

* Tue Dec 9 2014 Jeremy Newton <alexjnewt at hotmail dot com> - 4.0-6
- Patching for GCC 4.9

* Sat Dec 6 2014 Jeremy Newton <alexjnewt at hotmail dot com> - 4.0-5
- Line got deleted by accident, build fails

* Mon Oct 27 2014 Jeremy Newton <alexjnewt at hotmail dot com> - 4.0-4
- Change in wxGTK3-devel file
- Remove unnecessary CG requirement

* Thu Oct 2 2014 Jeremy Newton <alexjnewt at hotmail dot com> - 4.0-3
- Use polarssl 1.3 (fedora 21+) to avoid bundling
- patch to use entropy functionality in SSL instead of havege

* Thu Oct 2 2014 Jeremy Newton <alexjnewt at hotmail dot com> - 4.0-2
- Bundle polarssl (temporary fix, only for F19/20)

* Mon Mar 3 2014 Jeremy Newton <alexjnewt at hotmail dot com> - 4.0-1
- Update to dolphin 4.0.2
- Removed any unnecessary patches
- Added new and updated some old patches
- Removed exclusive arch, now builds on arm

* Wed Jan 1 2014 Jeremy Newton <alexjnewt at hotmail dot com> - 3.5-6
- Build for SDL2 (Adds vibration support)

* Mon Nov 18 2013 Jeremy Newton <alexjnewt at hotmail dot com> - 3.5-5
- Added patch for SFML, thanks to Hans de Goede

* Sat Jul 27 2013 Jeremy Newton <alexjnewt at hotmail dot com> - 3.5-4
- Updated for SFML compat

* Fri Jul 26 2013 Jeremy Newton <alexjnewt at hotmail dot com> - 3.5-3
-3 GCC 4.8 Fix (Fedora 19 and onwards)

* Tue Feb 19 2013 Jeremy Newton <alexjnewt at hotmail dot com> - 3.5-2
- Fixed date typos in SPEC

* Tue Feb 19 2013 Jeremy Newton <alexjnewt at hotmail dot com> - 3.5-1
- Updated to latest stable: removed GCC patch, updated CLRun patch
- Added patch to build on wxwidgets 2.8 (temporary workaround)

* Sat Feb 16 2013 Jeremy Newton <alexjnewt at hotmail dot com> - 3.0-12
- Removed patch for libav and disabled ffmpeg, caused rendering issues
- Minor consistency fixes to SPEC file

* Fri Dec 14 2012 Jeremy Newton <alexjnewt at hotmail dot com> - 3.0-11
- Added patch for recent libav api change in fc18, credit to Xiao-Long Chen
- Renamed patch 1 for consistency

* Mon Jun 25 2012 Jeremy Newton <alexjnewt at hotmail dot com> - 3.0-10
- Changed CLRun buildrequire package name
- Renamed GCC 4.7 patch to suit fedora standards
- Added missing hicolor-icon-theme require

* Sat Jun 02 2012 Xiao-Long Chen <chenxiaolong@cxl.epac.to> - 3.0-9
- Add patch to fix build with gcc 4.7.0 in fc17

* Thu Apr 5 2012 Jeremy Newton <alexjnewt at hotmail dot com> - 3.0-8
- Removed bundled CLRun

* Tue Mar 13 2012 Jeremy Newton <alexjnewt at hotmail dot com> - 3.0-7
- Removed bundled bochs
- Fixed get-source-from-git.sh: missing checkout 3.0

* Fri Feb 24 2012 Jeremy Newton <alexjnewt at hotmail dot com> - 3.0-6
- Removed purposeless zerolength file
Lots of clean up and additions, thanks to Xiao-Long Chen:
- Added man page
- Added script to grab source
- Added copyright file
- Added ExclusiveArch
- Added Some missing dependencies

* Thu Feb 23 2012 Jeremy Newton <alexjnewt at hotmail dot com> - 3.0-5
- Fixed Licensing
- Split sources and fixed source grab commands

* Fri Jan 27 2012 Jeremy Newton <alexjnewt at hotmail dot com> - 3.0-4
- Tweaked to now be able to encode frame dumps

* Sun Jan 22 2012 Jeremy Newton <alexjnewt at hotmail dot com> - 3.0-3
- Building now uses cmake macro
- Turned off building shared libs
- Removed unnecessary lines
- Fixed debuginfo-without-sources issue
- Reorganization of the SPEC for readability

* Thu Jan 12 2012 Jeremy Newton <alexjnewt at hotmail dot com> - 3.0-2
- Fixed up spec to Fedora Guidelines
- Fixed various trivial mistakes
- Added SOIL and SFML to dependancies
- Removed bundled SOIL and SFML from source spin

* Sun Dec 18 2011 Jeremy Newton <alexjnewt at hotmail dot com> - 3.0-1
- Initial package SPEC created
