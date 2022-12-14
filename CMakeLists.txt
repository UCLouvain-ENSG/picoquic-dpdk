cmake_minimum_required(VERSION 2.8.11)
cmake_policy(SET CMP0003 NEW)
project(picoquic C CXX)
find_package (Threads REQUIRED)
option(ENABLE_ASAN "Enable AddressSanitizer (ASAN) for debugging" OFF)
option(ENABLE_UBSAN "Enable UndefinedBehaviorSanitizer (UBSan) for debugging" OFF)

set(CMAKE_C_STANDARD 11)

message(STATUS "Initial CMAKE_C_FLAGS=${CMAKE_C_FLAGS}")

if(CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
    set(CMAKE_C_FLAGS "-std=gnu99 -ggdb -g -Wall -O3 -fno-exceptions -fno-signed-zeros -fno-trapping-math -march=native -msse4 -I/usr/local/include ${CC_WARNING_FLAGS} ${CMAKE_C_FLAGS}")
else()
    set(CMAKE_C_FLAGS "-std=gnu99 -ggdb -g -Wall -O3 -fno-exceptions -fno-signed-zeros -frename-registers -fno-trapping-math -march=native -msse4 -I/usr/local/include ${CC_WARNING_FLAGS} ${CMAKE_C_FLAGS}")
endif()

if(DISABLE_DEBUG_PRINTF)
    set(CMAKE_C_FLAGS "-DDISABLE_DEBUG_PRINTF ${CMAKE_C_FLAGS}")
endif()

include(CheckCCompilerFlag)
include(CheckCXXCompilerFlag)
include(CMakePushCheckState)

if(ENABLE_ASAN)
	cmake_push_check_state()
	set(CMAKE_REQUIRED_LIBRARIES "-fsanitize=address")
	check_c_compiler_flag(-fsanitize=address C__fsanitize_address_VALID)
	check_cxx_compiler_flag(-fsanitize=address CXX__fsanitize_address_VALID)
	cmake_pop_check_state()
	if(NOT C__fsanitize_address_VALID OR NOT CXX__fsanitize_address_VALID)
		message(FATAL_ERROR "ENABLE_ASAN was requested, but not supported!")
	endif()
	set(CMAKE_C_FLAGS "-fsanitize=address ${CMAKE_C_FLAGS}")
	set(CMAKE_CXX_FLAGS "-fsanitize=address ${CMAKE_CXX_FLAGS}")
endif()

if(ENABLE_UBSAN)
	cmake_push_check_state()
	set(CMAKE_REQUIRED_LIBRARIES "-fsanitize=undefined")
	check_c_compiler_flag(-fsanitize=undefined C__fsanitize_undefined_VALID)
	check_cxx_compiler_flag(-fsanitize=undefined CXX__fsanitize_undefined_VALID)
	cmake_pop_check_state()
	if(NOT C__fsanitize_undefined_VALID OR NOT CXX__fsanitize_undefined_VALID)
		message(FATAL_ERROR "ENABLE_UBSAN was requested, but not supported!")
	endif()
	set(CMAKE_C_FLAGS "-fsanitize=undefined ${CMAKE_C_FLAGS}")
	set(CMAKE_CXX_FLAGS "-fsanitize=undefined ${CMAKE_CXX_FLAGS}")

	# Ease detecting of "Runtime errors". If such an error is found, print a verbose
	# error report and exit the program
	cmake_push_check_state()
	set(CMAKE_REQUIRED_LIBRARIES "-fno-sanitize-recover")
	check_c_compiler_flag(-fno-sanitize-recover C__fnosanitize_recover_VALID)
	check_cxx_compiler_flag(-fno-sanitize-recover CXX__fnosanitize_recover_VALID)
	cmake_pop_check_state()
	if(NOT C__fnosanitize_recover_VALID OR NOT CXX__fnosanitize_recover_VALID)
		message(FATAL_ERROR "ENABLE_UBSAN was requested, but fno-sanitize-recover is not supported!")
	endif()
	set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fno-sanitize-recover")
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-sanitize-recover")
endif()

set(PICOQUIC_LIBRARY_FILES
    picoquic/bbr.c
    picoquic/bytestream.c
    picoquic/cc_common.c
    picoquic/config.c
    picoquic/cubic.c
    picoquic/fastcc.c
    picoquic/frames.c
    picoquic/intformat.c
    picoquic/logger.c
    picoquic/logwriter.c
    picoquic/newreno.c
    picoquic/packet.c
    picoquic/performance_log.c
    picoquic/picohash.c
    picoquic/picoquic_lb.c
    picoquic/picosocks.c
    picoquic/picosplay.c
    picoquic/quicctx.c
    picoquic/sacks.c
    picoquic/sender.c
    picoquic/sim_link.c
    picoquic/sockloop.c
    picoquic/sockloop_dpdk.c
    picoquic/spinbit.c
    picoquic/ticket_store.c
    picoquic/token_store.c
    picoquic/tls_api.c
    picoquic/transport.c
    picoquic/unified_log.c
    picoquic/util.c
)

set(PICOQUIC_CORE_HEADERS
     picoquic/picoquic.h
     picoquic/picosocks.h
     picoquic/picoquic_utils.h
     picoquic/picoquic_packet_loop.h
     picoquic/picoquic_unified_log.h
     picoquic/picoquic_logger.h
     picoquic/picoquic_binlog.h
     picoquic/picoquic_config.h
     picoquic/picoquic_lb.h
     )

set(LOGLIB_LIBRARY_FILES
    loglib/autoqlog.c
    loglib/cidset.c
    loglib/csv.c
    loglib/logconvert.c
    loglib/logreader.c
    loglib/qlog.c
    loglib/svg.c
)

set(LOGLIB_HEADERS 
     loglib/autoqlog.h)


set(PICOQUIC_TEST_LIBRARY_FILES
    picoquictest/ack_of_ack_test.c
    picoquictest/bytestream_test.c
    picoquictest/cert_verify_test.c
    picoquictest/cleartext_aead_test.c
    picoquictest/config_test.c
    picoquictest/cnx_creation_test.c
    picoquictest/cnxstress.c
    picoquictest/cplusplus.cpp
    picoquictest/datagram_tests.c
    picoquictest/edge_cases.c
    picoquictest/hashtest.c
    picoquictest/high_latency_test.c
    picoquictest/intformattest.c
    picoquictest/multipath_test.c
    picoquictest/netperf_test.c
    picoquictest/parseheadertest.c
    picoquictest/picoquic_lb_test.c
    picoquictest/pn2pn64test.c
    picoquictest/sacktest.c
    picoquictest/satellite_test.c
    picoquictest/skip_frame_test.c
    picoquictest/socket_test.c
    picoquictest/splay_test.c
    picoquictest/stream0_frame_test.c
    picoquictest/stresstest.c
    picoquictest/ticket_store_test.c
    picoquictest/tls_api_test.c
    picoquictest/transport_param_test.c
    picoquictest/util_test.c
)

set(PICOHTTP_LIBRARY_FILES
    picohttp/democlient.c
    picohttp/demoserver.c
    picohttp/h3zero.c
    picohttp/quicperf.c
	picohttp/siduck.c
    dpdk_proxy/proxy.c
)

set(PICOHTTP_HEADERS
     picohttp/h3zero.h
     picohttp/democlient.h
     picohttp/demoserver.h
     dpdk_proxy/proxy.h)
     
set(DPDK_PICOQUIC_DEMO_HEADERS
    dpdk_picoquicdemo/dpdk_picoquicdemo.h)

set(PICOHTTP_TEST_LIBRARY_FILES
    picoquictest/h3zerotest.c
)

set(CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
find_package(PTLS REQUIRED)
message(STATUS "picotls/include: ${PTLS_INCLUDE_DIRS}" )
message(STATUS "picotls libraries: ${PTLS_LIBRARIES}" )

OPTION(PTLS_WITH_FUSION "build 'fusion' AES-GCM engine" ${PTLS_WITH_FUSION_DEFAULT})
if(PTLS_WITH_FUSION)
    message(STATUS "PTLS Fusion is enabled")
else()
    message(STATUS "PTLS compiled without support for Fusion")
	set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -DPTLS_WITHOUT_FUSION")
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DPTLS_WITHOUT_FUSION")
endif()

find_package(OpenSSL )
message(STATUS "root: ${OPENSSL_ROOT_DIR}")
message(STATUS "OpenSSL_VERSION: ${OPENSSL_VERSION}")
message(STATUS "OpenSSL_INCLUDE_DIR: ${OPENSSL_INCLUDE_DIR}")
message(STATUS "OpenSSL_LIBRARIES: ${OPENSSL_LIBRARIES}")
message(STATUS "CMAKE_C_FLAGS: ${CMAKE_C_FLAGS}")
message(STATUS "CMAKE_CXX_FLAGS: ${CMAKE_CXX_FLAGS}")

include_directories(picoquic picoquictest
    ${PTLS_INCLUDE_DIRS} ${OPENSSL_INCLUDE_DIR})

add_library(picoquic-core ${PICOQUIC_CORE_HEADERS}
    ${PICOQUIC_LIBRARY_FILES}
)


find_package(PkgConfig REQUIRED)
pkg_check_modules(LIBDPDK REQUIRED IMPORTED_TARGET libdpdk)

target_link_libraries(picoquic-core PUBLIC
    ${PTLS_LIBRARIES}
    ${OPENSSL_LIBRARIES}
    PkgConfig::LIBDPDK
)

add_library(picoquic-log
    ${LOGLIB_LIBRARY_FILES}
)

target_link_libraries(picoquic-log PUBLIC
    PkgConfig::LIBDPDK
)


add_library(picohttp-core
    ${PICOHTTP_LIBRARY_FILES}
)

target_link_libraries(picohttp-core
    ${PTLS_LIBRARIES}
    ${OPENSSL_LIBRARIES}
    PkgConfig::LIBDPDK
)

add_executable(picoquicdemo
    picoquicfirst/picoquicdemo.c
    picoquicfirst/getopt.c
)

# dpdk_picoquicdemo
add_executable(dpdk_picoquicdemo
    dpdk_picoquicfirst/dpdk_picoquicdemo.c
    dpdk_picoquicfirst/getopt.c
    dpdk_picoquicfirst/dpdk_client.c
    dpdk_picoquicfirst/dpdk_server.c
)

target_link_libraries(picoquicdemo
    picoquic-log
    picoquic-core
    picohttp-core
    ${PTLS_LIBRARIES}
    ${OPENSSL_LIBRARIES}
    ${CMAKE_DL_LIBS}
    ${CMAKE_THREAD_LIBS_INIT}
    PkgConfig::LIBDPDK
)

target_link_libraries(dpdk_picoquicdemo
    picoquic-log
    picoquic-core
    picohttp-core
    ${PTLS_LIBRARIES}
    ${OPENSSL_LIBRARIES}
    ${CMAKE_DL_LIBS}
    ${CMAKE_THREAD_LIBS_INIT}
    PkgConfig::LIBDPDK
)

target_include_directories(picoquicdemo PRIVATE loglib picohttp)
target_include_directories(dpdk_picoquicdemo PRIVATE loglib picohttp)
target_include_directories(dpdk_picoquicdemo PRIVATE loglib dpdk_proxy)

# udp sender

add_executable(udpsender
    dpdk_proxy/udpsender.c
    dpdk_proxy/token_bucket.c
)

target_link_libraries(udpsender
    picoquic-core
    ${PTLS_LIBRARIES}
    ${OPENSSL_LIBRARIES}
    ${CMAKE_DL_LIBS}
    ${CMAKE_THREAD_LIBS_INIT}
    PkgConfig::LIBDPDK
)

# udp receiver

add_executable(udpreceiver
    dpdk_proxy/udpreceiver.c
)

target_link_libraries(udpreceiver
    picoquic-core
    ${PTLS_LIBRARIES}
    ${OPENSSL_LIBRARIES}
    ${CMAKE_DL_LIBS}
    ${CMAKE_THREAD_LIBS_INIT}
    PkgConfig::LIBDPDK
)

add_executable(simple_proxy
    dpdk_proxy/simple_proxy.c
)

target_link_libraries(simple_proxy
    picoquic-core
    ${PTLS_LIBRARIES}
    ${OPENSSL_LIBRARIES}
    ${CMAKE_DL_LIBS}
    ${CMAKE_THREAD_LIBS_INIT}
    PkgConfig::LIBDPDK
)


add_executable(picolog_t
    picolog/picolog.c
)

target_link_libraries(picolog_t
    picoquic-log
    picoquic-core
    ${PTLS_LIBRARIES}
    ${OPENSSL_LIBRARIES}
    ${CMAKE_DL_LIBS}
    ${CMAKE_THREAD_LIBS_INIT}
    PkgConfig::LIBDPDK
)

target_include_directories(picolog_t PRIVATE loglib)

add_executable(picoquic_ct picoquic_t/picoquic_t.c
    ${PICOQUIC_TEST_LIBRARY_FILES}
)

target_link_libraries(picoquic_ct
    picoquic-log
    picoquic-core
    ${PTLS_LIBRARIES}
    ${OPENSSL_LIBRARIES}
    ${CMAKE_DL_LIBS}
    ${CMAKE_THREAD_LIBS_INIT}
    PkgConfig::LIBDPDK
)

target_include_directories(picoquic_ct PRIVATE loglib)

add_executable(picohttp_ct picohttp_t/picohttp_t.c
    ${PICOQUIC_TEST_LIBRARY_FILES}
    ${PICOHTTP_TEST_LIBRARY_FILES}
)

target_link_libraries(picohttp_ct
    picoquic-log
    picoquic-core
    picohttp-core
    ${PTLS_LIBRARIES}
    ${OPENSSL_LIBRARIES}
    ${CMAKE_DL_LIBS}
    ${CMAKE_THREAD_LIBS_INIT}
    PkgConfig::LIBDPDK
)

target_include_directories(picohttp_ct PRIVATE loglib picohttp)

set(TEST_EXES picoquic_ct picohttp_ct)

# get all project files for formatting
file(GLOB_RECURSE CLANG_FORMAT_SOURCE_FILES *.c *.h)

# Adds clangformat as target that formats all source files
add_custom_target(
    clangformat
    COMMAND clang-format
    -style=Webkit
    -i
    ${CLANG_FORMAT_SOURCE_FILES}
)

# Specify Install targets
install(TARGETS picoquicdemo picolog_t picoquic-core picoquic-log picohttp-core
        RUNTIME DESTINATION bin
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib
)

install(FILES
        ${PICOQUIC_CORE_HEADERS}
        ${PICOQUIC_LOGLIB_HEADERS}
        ${PICOHTTP_HEADERS}
        ${DPDK_PICOQUIC_DEMO_HEADERS}
        DESTINATION include)
