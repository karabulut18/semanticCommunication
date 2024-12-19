find_package(PkgConfig)

PKG_CHECK_MODULES(PC_GR_CUSTOM gnuradio-custom)

FIND_PATH(
    GR_CUSTOM_INCLUDE_DIRS
    NAMES gnuradio/custom/api.h
    HINTS $ENV{CUSTOM_DIR}/include
        ${PC_CUSTOM_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    GR_CUSTOM_LIBRARIES
    NAMES gnuradio-custom
    HINTS $ENV{CUSTOM_DIR}/lib
        ${PC_CUSTOM_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/gnuradio-customTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(GR_CUSTOM DEFAULT_MSG GR_CUSTOM_LIBRARIES GR_CUSTOM_INCLUDE_DIRS)
MARK_AS_ADVANCED(GR_CUSTOM_LIBRARIES GR_CUSTOM_INCLUDE_DIRS)
