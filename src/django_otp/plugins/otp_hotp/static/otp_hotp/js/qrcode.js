function ready(fn) {
    if (document.readyState !== 'loading') {
        fn();
    } else {
        document.addEventListener('DOMContentLoaded', fn);
    }
}

ready(function () {
    var qrCodeImage = document.querySelector('.qrcode-image');
    if (!qrCodeImage) {
        return;
    }
    qrCodeImage.addEventListener('error', function () {
        var qrCode = document.getElementById('qrcode');
        var noQrCode = document.getElementById('no-qrcode');
        if (qrCode) {
            qrCode.classList.add('qrcode-hidden');
        }
        if (noQrCode) {
            noQrCode.classList.remove('qrcode-hidden');
        }
    });
});
