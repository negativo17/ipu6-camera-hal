%global commit 8863bda8b15bef415f112700d0fb04e00a48dbee
%global date 20240719
%global shortcommit %(c=%{commit}; echo ${c:0:7})

# We want to specify multiple separate build-dirs for the different variants
%global __cmake_in_source_build 1

Name:           ipu6-camera-hal
Summary:        IPU6 Hardware Abstraction Layer
Version:        0
Release:        7.%{date}git%{shortcommit}%{?dist}
License:        Apache-2.0
URL:            https://github.com/intel/ipu6-camera-hal
ExclusiveArch:  x86_64

Source0:        https://github.com/intel/%{name}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz
Source1:        60-intel-ipu6.rules
Patch0:         https://github.com/intel/ipu6-camera-hal/pull/113.patch
Patch1:         %{name}-path.patch

BuildRequires:  cmake
BuildRequires:  expat-devel
BuildRequires:  gcc
BuildRequires:  g++
BuildRequires:  ipu6-camera-bins-devel
BuildRequires:  kernel-headers
BuildRequires:  libdrm-devel
BuildRequires:  systemd-rpm-macros

Provides:       ipu6-driver = %{version}
Provides:       ipu6-kmod-common = %{version}

Requires:       ipu6-camera-bins%{?_isa}
Requires:       ipu6-kmod

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
for target in ipu_tgl ipu_adl ipu_mtl; do
  export PKG_CONFIG_PATH=%{_libdir}/$target/pkgconfig/
  mkdir $target
  pushd $target
    [[ "$target" = "ipu_tgl" ]] && IPU_VERSION=ipu6
    [[ "$target" = "ipu_adl" ]] && IPU_VERSION=ipu6ep
    [[ "$target" = "ipu_mtl" ]] && IPU_VERSION=ipu6epmtl
    sed -i -e "s|CAMERA_DEFAULT_CFG_PATH.*|CAMERA_DEFAULT_CFG_PATH \"%{_datadir}/camera/\"|g" \
      ../src/platformdata/PlatformData.h
    %cmake \
      -DBUILD_CAMHAL_TESTS=OFF \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_SUB_PATH=$target \
      -DCMAKE_INSTALL_SYSCONFDIR=%{_datadir} \
      -DIPU_VER=$IPU_VERSION \
      -DUSE_PG_LITE_PIPE=ON \
      ..
    %cmake_build
  popd
done

mkdir hal_adaptor
pushd hal_adaptor
  export PKG_CONFIG_PATH=%{_libdir}/pkgconfig/
  %cmake ../src/hal/hal_adaptor
  %cmake_build
popd

%install
for target in ipu_tgl ipu_adl ipu_mtl hal_adaptor; do
  pushd $target
    %cmake_install
    rm -f %{buildroot}%{_libdir}/$target/libcamhal.a
    rm -fr %{buildroot}%{_libdir}/$target/pkgconfig
  popd
done

install -p -m 0644 -D %{SOURCE1} %{buildroot}%{_udevrulesdir}/60-intel-ipu6.rules

%files
%license LICENSE
%ghost %config %{_sysconfdir}/ld.so.conf.d/ipu6-%{_target_cpu}.conf
%dir %{_datadir}/camera
%{_datadir}/camera/ipu_adl
%{_datadir}/camera/ipu_mtl
%{_datadir}/camera/ipu_tgl
%{_libdir}/ipu_adl/libcamhal.so.0.0.0
%{_libdir}/ipu_adl/libcamhal.so.0
%{_libdir}/ipu_adl/libcamhal.so
%{_libdir}/ipu_mtl/libcamhal.so.0.0.0
%{_libdir}/ipu_mtl/libcamhal.so.0
%{_libdir}/ipu_mtl/libcamhal.so
%{_libdir}/ipu_tgl/libcamhal.so.0.0.0
%{_libdir}/ipu_tgl/libcamhal.so.0
%{_libdir}/ipu_tgl/libcamhal.so
%{_libdir}/libhal_adaptor.so.0.0.0
%{_libdir}/libhal_adaptor.so.0
%{_udevrulesdir}/60-intel-ipu6.rules

%files devel
%{_includedir}/hal_adaptor
%{_libdir}/libhal_adaptor.so
%{_libdir}/pkgconfig/hal_adaptor.pc

%changelog
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
