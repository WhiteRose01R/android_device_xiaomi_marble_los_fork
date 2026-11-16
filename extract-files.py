#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

from pathlib import Path
import sys

from extract_utils.fixups_blob import (
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.fixups_lib import (
    lib_fixups,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[1]
        / 'sm8450-common/sensors/sensor-notifier/udals'
    ),
)
from extract_model import fixup_model

UDALS_SPEC = {
    'sha256': '186d5f610b9eb996242151b28f21c64d14b5452bd513fe57df019ae184a66577',
    'grid': 19,
    'block_size': 5,
    'gamma': {'addr': 0x112350},
    'msg_unknown1': 2,
    'sensor_owner': 'sns_tcs3701',
    'spatial': [0x116C40, 0x117788, 0x1182D0],
    'input_transform': 'affine',
    'input_offset': [10.0, 0.0, 0.0, 0.0],
    'input_divisor': [
        2037.0,
        {'addr': 0x112318},
        111953536.0,
        {'addr': 0x1123B8},
    ],
    'routing': 'per_channel',
    'dc_curve_max_dbv': 0,
    'networks': [
        {
            'base': 0x118E48,
            'layers': [128, 64, 32, 1],
            'output_bias': [{'addr': 0x112338}],
            'exponent': [{'addr': 0x1123F0}],
            'divisor': [{'addr': 0x1123D8}],
            'negative': 'allow',
        },
        {
            'base': 0x12E648,
            'layers': [128, 64, 32, 1],
            'output_bias': [{'addr': 0x1123C0}],
            'exponent': [{'addr': 0x112330}],
            'divisor': [{'addr': 0x112378}],
            'negative': 'allow',
        },
        {
            'base': 0x143E48,
            'layers': [128, 64, 32, 1],
            'output_bias': [{'addr': 0x112410}],
            'exponent': [4.25],
            'divisor': [{'addr': 0x1123C8}],
            'negative': 'allow',
        },
        {
            'base': 0x159648,
            'layers': [128, 64, 32, 1],
            'output_bias': [{'addr': 0x112408}],
            'exponent': [{'addr': 0x112320}],
            'divisor': [{'addr': 0x1123E8}],
            'negative': 'allow',
        },
    ],
    'lux': {
        'coef_scale': True,
        'divisor': 51200.0,
        'saturation_raw': 16775000.0,
        'saturation_lux': 200000.0,
    },
    'filter': {
        'median_window': 3,
        'deadband_strict_less': True,
        'deadband_tiers': [{'ratio': 0.05}],
    },
}

namespace_imports = [
    'device/xiaomi/sm8450-common',
    'hardware/qcom-caf/sm8450',
    'hardware/xiaomi',
    'vendor/qcom/opensource/commonsys-intf/display',
    'vendor/xiaomi/sm8450-common',
]

blob_fixups: blob_fixups_user_type = {
    'vendor/lib64/hw/camera.qcom.so': blob_fixup()
        .add_needed('libcamximageformatutils_shim.so'),
    (
        'vendor/etc/camera/marble_enhance_motiontuning.xml',
        'vendor/etc/camera/marble_motiontuning.xml',
    ): blob_fixup().regex_replace('xml=version', 'xml version'),
    'vendor/etc/camera/pureView_parameter.xml': blob_fixup().regex_replace(
        r'=([0-9]+)>', r'="\1">'
    ),
    'vendor/etc/sensors/udals-model.json': blob_fixup().call(
        fixup_model, UDALS_SPEC
    ),
    (
        'vendor/lib64/camera/plugins/com.xiaomi.plugin.mialgosnsc.so',
        'vendor/lib64/com.qti.feature2.anchorsync.so',
    ): blob_fixup().replace_needed('libtinyxml2.so', 'libtinyxml2-v34.so'),
    (
        'vendor/lib64/hw/com.qti.chi.override.so',
        'vendor/lib64/libcamxcommonutils.so',
        'vendor/lib64/libmialgoengine.so',
    ): blob_fixup().add_needed('libprocessgroup_shim.so'),
    'vendor/lib64/libgf_hal.so': blob_fixup().binary_regex_replace(
        rb'\[%s\] openat: %s xiaomi_sysfs_fd,failed:\[fingerdown\]',
        b'[%s] openat: xiaomi_sysfs_fd,failed:[fingerdown]\x00\x00\x00',
    ),
    (
        'vendor/lib64/libTrueSight.so',
        'vendor/lib64/libalLDC.so',
        'vendor/lib64/libalhLDC.so',
    ): blob_fixup()
    .clear_symbol_version('AHardwareBuffer_allocate')
    .clear_symbol_version('AHardwareBuffer_describe')
    .clear_symbol_version('AHardwareBuffer_lock')
    .clear_symbol_version('AHardwareBuffer_lockPlanes')
    .clear_symbol_version('AHardwareBuffer_release')
    .clear_symbol_version('AHardwareBuffer_unlock'),
}

module = ExtractUtilsModule(
    'marble',
    'xiaomi',
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
    namespace_imports=namespace_imports,
    add_firmware_proprietary_file=True,
)

if __name__ == '__main__':
    utils = ExtractUtils.device_with_common(
        module, 'sm8450-common', module.vendor
    )
    utils.run()
