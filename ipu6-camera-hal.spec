%global commit 9899efa70921906ee6dd23c9f83aff343968f164
%global date 20260120
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           ipu6-camera-hal
Summary:        IPU6 Hardware Abstraction Layer
Version:        0^%{date}git%{shortcommit}
Release:        17%{?dist}
License:        Apache-2.0
URL:            https://github.com/intel/ipu6-camera-hal
ExclusiveArch:  x86_64

Source0:        https://github.com/intel/%{name}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz
Source1:        72-ipu6-psys.rules
Source2:        50-ipu6-hide-raw-v4l2.conf

BuildRequires:  cmake
BuildRequires:  expat-devel
BuildRequires:  gcc
BuildRequires:  g++
BuildRequires:  ipu6-camera-bins-devel
BuildRequires:  kernel-headers
BuildRequires:  libdrm-devel
BuildRequires:  systemd-rpm-macros

# Components do not have matching snapshots, so just use something to satisfy dependencies:
Provides:       ipu6-kmod-common = 1

Requires:       ipu6-camera-bins%{?_isa}
Requires:       ipu6-kmod
Requires:       libcamhal%{?_isa}
Requires:       wireplumber

%description
IPU6 Hardware Abstraction Layer plugins. They support MIPI cameras through the
IPU6 on Intel Tiger Lake, Alder Lake, Raptor Lake and Meteor Lake platforms. The
plugins are loaded on demand by the libcamhal adaptor, which is provided by the
libcamhal package.

%prep
%autosetup -p1 -n %{name}-%{commit}

%build
export CFLAGS="%{optflags} -Wno-error=unused-but-set-variable"
export CXXFLAGS="%{optflags} -Wno-error=alloc-size-larger-than=9223372036854775807 -Wno-error=unused-but-set-variable"
%cmake \
  -DBUILD_CAMHAL_ADAPTOR=OFF \
  -DBUILD_CAMHAL_PLUGIN=ON \
  -DBUILD_CAMHAL_TESTS=OFF \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_SYSCONFDIR=%{_datadir} \
  -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
  -DIPU_VERSIONS="ipu6;ipu6ep;ipu6epmtl" \
  -DUSE_PG_LITE_PIPE=ON

%cmake_build

%install
%cmake_install

install -p -m 0644 -D %{SOURCE1} %{buildroot}%{_udevrulesdir}/72-ipu6-psys.rules

# Load the PSYS module at boot so /dev/ipu-psys0 is available (it does not
# auto-load):
install -d %{buildroot}%{_modulesloaddir}
echo intel-ipu6-psys > %{buildroot}%{_modulesloaddir}/ipu6-psys.conf

# Filter out raw v4l2 devices (not usable) from the list of available cameras in Pipewire:
install -p -m 0644 -D %{SOURCE2} %{buildroot}%{_datadir}/wireplumber/wireplumber.conf.d/50-ipu6-hide-raw-v4l2.conf

%post
%systemd_user_post wireplumber.service

%postun
%systemd_user_postun_with_restart wireplumber.service

%files
%license LICENSE
%doc README.md SECURITY.md
%{_datadir}/camera/
%{_libdir}/libcamhal/
%{_modulesloaddir}/ipu6-psys.conf
%{_udevrulesdir}/72-ipu6-psys.rules
%{_datadir}/wireplumber/wireplumber.conf.d/50-ipu6-hide-raw-v4l2.conf

%changelog
* Mon Jul 13 2026 Simone Caronni <negativo17@gmail.com> - 0^20260120git9899efa-17
- Add wireplumber configuration to hide raw v4l2 devices.

* Thu Jul 09 2026 Simone Caronni <negativo17@gmail.com> - 0^20260120git9899efa-16
- Load the intel-ipu6-psys module at boot through modules-load.d.

* Wed Jul 08 2026 Simone Caronni <negativo17@gmail.com> - 0^20260120git9899efa-15
- Add docs.

* Wed Jul 08 2026 Simone Caronni <negativo17@gmail.com> - 0^20260120git9899efa-14
- Build only the IPU6 HAL plugins; the libcamhal adaptor and headers are now
  provided by the shared libcamhal / libcamhal-devel packages built from
  ipu7-camera-hal.

* Tue Jul 07 2026 Simone Caronni <negativo17@gmail.com> - 0^20260120git9899efa-13
- Adjust dependencies.

* Mon Jul 06 2026 Simone Caronni <negativo17@gmail.com> - 0^20260120git9899efa-12
- Add udev rule for intel-ipu6-psys device.

* Mon Jul 06 2026 Simone Caronni <negativo17@gmail.com> - 0^20260120git9899efa-11
- Update to latest snapshot.
- Use proper snapshot format.

* Fri Jun 27 2025 Simone Caronni <negativo17@gmail.com> - 0-10.20250627gitc933525
- Update to latest snapshot.

* Mon Nov 25 2024 Simone Caronni <negativo17@gmail.com> - 0-9.20241115git7527bcc
- Update to latest snapshot.

* Sun Oct 27 2024 Simone Caronni <negativo17@gmail.com> - 0-8.20241012gita2de9c2
- Update to latest snapshot. Unified build.

* Tue Aug 06 2024 Simone Caronni <negativo17@gmail.com> - 0-7.20240719git8863bda
- Update to latest snapshot.

* Thu Jul 04 2024 Simone Caronni <negativo17@gmail.com> - 0-6.20240509git289e645
- Add new patches.
- Adjust devel subpackage.
- Add PCI ID for Meteor Lake.

* Sat Jun 22 2024 Simone Caronni <negativo17@gmail.com> - 0-5.20240509git289e645
- Adjust file lists.

* Fri Jun 21 2024 Simone Caronni <negativo17@gmail.com> - 0-4.20240509git289e645
- VSC is part of the IPU6 kernel module package.

* Mon May 13 2024 Simone Caronni <negativo17@gmail.com> - 0-3.20240509git289e645
- Update to latest snapshot.

* Wed May 08 2024 Simone Caronni <negativo17@gmail.com> - 0-2.20240411gitf073cb6
- Add LD configuration as ghost file.

* Mon May 06 2024 Simone Caronni <negativo17@gmail.com> - 0-1.20240416gitf073cb6
- First build.
