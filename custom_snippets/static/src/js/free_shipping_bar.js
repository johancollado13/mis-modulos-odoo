/** @odoo-module */

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.FreeShippingBar = publicWidget.Widget.extend({
    selector: '#wrapwrap', 
    
    start: function () {
        this._super.apply(this, arguments);
        // Le damos un pequeño tiempo de espera para asegurar que el subtotal ya cargó en pantalla
        setTimeout(() => {
            this.calculateFreeShipping();
        }, 300);
    },

    calculateFreeShipping: function () {
        // Buscamos el subtotal limpio en el resumen de Odoo
        const subtotalElement = document.querySelector('#order_total_untaxed .oe_currency_value, #order_total .oe_currency_value, .o_wsale_total .oe_currency_value');
        if (!subtotalElement) return;

        let rawText = subtotalElement.textContent || subtotalElement.innerText;
        const currentTotal = parseFloat(rawText.replace(/,/g, '').trim());
        
        if (isNaN(currentTotal)) return;

        const targetAmount = 3000; // Tu meta de RD$3,000
        
        let percentage = (currentTotal / targetAmount) * 100;
        if (percentage > 100) percentage = 100;

        let remaining = targetAmount - currentTotal;
        let message = '';
        let barClass = 'bg-info';

        if (remaining > 0) {
            message = `¡Estás a solo <strong>RD$ ${remaining.toLocaleString('en-US', {minimumFractionDigits: 2})}</strong> de conseguir <strong>Envío Gratis</strong>!`;
        } else {
            message = `🎉 ¡Felicidades! Tu envío es totalmente <strong>GRATIS</strong>`;
            barClass = 'bg-success progress-bar-striped progress-bar-animated';
        }

        const barHtml = `
            <div class="custom-free-shipping-box mb-4 p-3 border rounded bg-white shadow-sm" style="border-left: 4px solid #17a2b8 !important; clear: both;">
                <p class="text-center mb-2 text-dark" style="font-size: 13px; font-family: sans-serif;">${message}</p>
                <div class="progress" style="height: 10px; border-radius: 10px; background-color: #e9ecef;">
                    <div class="progress-bar ${barClass}" role="progressbar" 
                         style="width: ${percentage}%; transition: width 0.8s ease;" 
                         aria-valuenow="${percentage}" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
            </div>
        `;

        // Limpieza para evitar duplicados si el usuario cambia cantidades
        const oldBar = document.querySelector('.custom-free-shipping-box');
        if (oldBar) oldBar.remove();

        // EL TRUCO: Buscamos la caja contenedora del resumen que comparten el carrito y el pago
        const cartSummary = document.querySelector('.js_cart_summary, #o_wsale_total_accordion, .o_wsale_total');

        if (cartSummary) {
            // Lo metemos justo al principio de la tarjeta del total para que se vea arriba
            cartSummary.insertAdjacentHTML('afterbegin', barHtml);
        }
    }
});

export default publicWidget.registry.FreeShippingBar;