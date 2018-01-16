/*
@author Ronan Delacroix
*/

$(document).ready(function() {

    Vue.component('transaction-item', {
        props: ['t'],
        template: '<tr v-bind:title="t.hash"><td>{{ t.time }}</td><td>{{ t.amount }}</td><td>{{ t.fee }}</td><td>{{ t.mixin }}</td></tr>',
    });

    var app = new Vue({
        el: '#wallet',
        data: {
            message: '',
            loading: false,
            price : {
                usd: 1.0,
                percent_change_24h: "0"
            },
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
                    $.notify(vm.message, 'info');
                }).catch(function(error) {
                    vm.message = 'Error ' + error;
                    $.notify(vm.message, {className:'error', autoHideDelay: 10000});
                }).finally(function() {
                    vm.loading = false;
                });

                axios.get('https://api.coinmarketcap.com/v1/ticker/').then(function (response) {
                    var electroneum = _.where(response.data, {id: 'electroneum'})[0];
                    vm.price.usd = electroneum.price_usd;
                    vm.price.percent_change_24h = electroneum.percent_change_24h;
                }).catch(function(error) {
                    vm.message = vm.message + 'Error ' + error;
                    $.notify(vm.message, {className:'error', autoHideDelay: 10000});
                })


                setTimeout(this.refreshWallet, 10000);
            }
        }
    });

});
