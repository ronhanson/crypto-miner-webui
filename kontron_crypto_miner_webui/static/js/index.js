/*
@author Ronan Delacroix
*/

$(document).ready(function() {

    Vue.component('transaction-item', {
        props: ['transaction'],
        template: '<tr><td v-bind:title="transaction.hash">{{ transaction.time }}</td><td>{{ transaction.amount }}</td><td>{{ transaction.fee }}</td><td>{{ transaction.mixin }}</td></tr>',
    });

    var app = new Vue({
        el: '#wallet',
        data: {
            message: '',
            loading: false,
            stats : {
                hashes: 0,
                hashrate: '---',
                paid: 0,
                balance: 0,
                lastShare: '---'
            },
            transactions: [
            ]
        },
        created: function() {
            this.refreshWallet();
        },
        methods: {
            refreshWallet: function() {
                this.message = 'Loading...';
                this.loading = true;
                var vm = this;
                axios.get('https://api.electromine.fr/stats_address?address='+WALLET_ADDRESS).then(function (response) {
                    vm.stats = response.data.stats;
                    vm.stats.lastShare = moment(vm.stats.lastShare*1000).calendar()

                    var transactions = [];
                    var payments = response.data.payments;

                    for (var i = 0; i < payments.length; i += 2) {
                        var p = payments[i];
                        var parts = p.split(':');
                        var payment = {
                            time: moment(payments[i + 1]*1000).calendar(),
                            hash: parts[0],
                            amount: (parts[1]/100.0).toFixed(2) + ' ETN',
                            fee: (parts[2]/100.0).toFixed(2) + ' ETN',
                            mixin: parts[3]
                        };
                        transactions.push(payment);
                    }
                    vm.transactions = transactions;
                    vm.message = 'Wallet loaded';
                    $.notify(vm.message, 'success');
                }).catch(function(error) {
                    vm.message = 'Error ' + error;
                    $.notify(vm.message, 'error');
                }).finally(function() {
                    vm.loading = false;
                });
            }
        }
    });

});
