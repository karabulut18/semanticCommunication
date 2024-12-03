INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_MYBLOCKS myBlocks)

FIND_PATH(
    MYBLOCKS_INCLUDE_DIRS
    NAMES myBlocks/api.h
    HINTS $ENV{MYBLOCKS_DIR}/include
        ${PC_MYBLOCKS_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    MYBLOCKS_LIBRARIES
    NAMES gnuradio-myBlocks
    HINTS $ENV{MYBLOCKS_DIR}/lib
        ${PC_MYBLOCKS_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/myBlocksTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(MYBLOCKS DEFAULT_MSG MYBLOCKS_LIBRARIES MYBLOCKS_INCLUDE_DIRS)
MARK_AS_ADVANCED(MYBLOCKS_LIBRARIES MYBLOCKS_INCLUDE_DIRS)
