
document.addEventListener('DOMContentLoaded', function () {

    
    const messages = document.querySelectorAll('.msg');
    messages.forEach(msg => {
        setTimeout(() => {
            msg.style.transition = 'opacity 0.5s ease';
            msg.style.opacity = '0';
            setTimeout(() => msg.remove(), 500);
        }, 4000);
    });

    // Confirm on withdraw/transfer submit
    const withdrawForm = document.querySelector('form[action*="withdraw"]');
    if (withdrawForm) {
        withdrawForm.addEventListener('submit', function (e) {
            const amount = document.querySelector('input[name="amount"]').value;
            if (!confirm(`Confirm withdrawal of ₹${amount}?`)) e.preventDefault();
        });
    }

    const transferForm = document.querySelector('form[action*="transfer"]');
    if (transferForm) {
        transferForm.addEventListener('submit', function (e) {
            const amount = document.querySelector('input[name="amount"]').value;
            const accNo = document.querySelector('input[name="account_number"]').value;
            if (!confirm(`Transfer ₹${amount} to account ${accNo}?`)) e.preventDefault();
        });
    }

    // Format amount input with commas (display only)
    const amountInput = document.getElementById('amountInput');
    if (amountInput) {
        amountInput.addEventListener('focus', function () {
            this.select();
        });
    }
});
