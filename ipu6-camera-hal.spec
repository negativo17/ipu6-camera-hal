%global commit 7527bcc0a078fb5a8ea4da9eabf7866ddfb0da3d
%global date 20241115
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           ipu6-camera-hal
Summary:        IPU6 Hardware Abstraction Layer
Version:        0
Release:        9.%{date}git%{shortcommit}%{?dist}
License:        Apache-2.0
URL:            https://github.com/intel/ipu6-camera-hal
ExclusiveArch:  x86_64

Source0:        https://github.com/intel/%{name}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz

BuildRequires:  cmake
BuildRequires:  expat-devel
BuildRequires:  gcc
BuildRequires:  g++
BuildRequires:  ipu6-camera-bins-devel
BuildRequires:  kernel-headers
BuildRequires:  libdrm-devel
BuildRequires:  systemd-rpm-macros

Provides:       ipu6-kmod-common = %{version}

Requires:       ipu6-camera-bins%{?_isa}

%description
IPU6 Hardware Abstraction Layer. It supports MIPI cameras through the IPU6 on
Intel Tiger Lake, Alder Lake, Raptor Lake and Meteor Lake platforms.

%package devel
Summary:        IPU6 header files for HAL
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       ipu6-camera-bins-devel

%description devel
This provides the necessary header files for IPU6 HAL development.

%prep
%autosetup -p1 -n %{name}-%{commit}

%build
%cmake \
  -DBUILD_CAMHAL_ADAPTOR=ON \
  -DBUILD_CAMHAL_PLUGIN=ON \
  -DBUILD_CAMHAL_TESTS=OFF \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_SYSCONFDIR=%{_datadir} \
  -DIPU_VERSIONS="ipu6;ipu6ep;ipu6epmtl" \
  -DUSE_PG_LITE_PIPE=ON

%cmake_build

%install
%cmake_install

%files
%license LICENSE
%{_datadir}/camera/
%{_libdir}/libcamhal.so.0.0.0
%{_libdir}/libcamhal.so.0
%{_libdir}/libcamhal/

%files devel
%{_includedir}/libcamhal/
%{_libdir}/libcamhal.so
%{_libdir}/pkgconfig/libcamhal.pc

%changelog
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
