/*
@author Ronan Delacroix
*/


$(document).ready(function() {

    function refresh_wallet() {
        this.message = 'Loading...';
        this.loading = true;
        var vm = this;
        axios.get('https://api.electromine.fr/stats_address?address='+WALLET_ADDRESS).then(function (response) {
            vm.stats = response.data.stats;
            vm.stats.lastShare = moment(vm.stats.lastShare*1000).calendar()

            var graph_x_dates = [];
            var graph_y_values = [];
            /*var graph_y_top_value =0;*/
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
                graph_x_dates.push(moment(payments[i + 1]*1000).toISOString())
                /*graph_y_top_value = graph_y_top_value+(parts[1]/100.0)*/
                graph_y_values.push(parts[1]/100.0)
            }
            vm.transactions = transactions;
            vm.message = 'Wallet loaded';

            graph_x_dates = graph_x_dates.reverse();
            graph_y_values = graph_y_values.reverse();
            var last_val = 0;
            var graph_y_stacked_values = _.map(graph_y_values, function(val) {
                last_val = last_val + val;
                return last_val;
            });
            var graph_data = [{
                x: graph_x_dates,
                y: graph_y_stacked_values,
                name: 'Balance over time (ETN)',
                fill: 'tonexty',
                type: 'scatter'
            },{
                x: graph_x_dates,
                y: graph_y_values,
                marker: {
                    color:'rgb(188, 208, 220)',
                    size:graph_y_values,
                },
                name: 'Payments (ETN)',
                yaxis: 'y2',
                mode: 'markers',
                type: 'scatter'
            }];
            var layout = {
                title: 'Eletromine Payments',
                yaxis: {title: 'Overall Balance (ETN)'},
                yaxis2: {
                    title: 'Payments (ETN)',
                    titlefont: {color: 'rgb(188, 208, 220)'},
                    tickfont: {color: 'rgb(188, 208, 220)'},
                    overlaying: 'y',
                    side: 'right'
                }
            };
            Plotly.newPlot('transactions_graph', graph_data, layout);
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
        });

        setTimeout(this.refreshWallet, 10000);
    }

    Vue.config.delimiters = ['[[', ']]'];

    TransactionItem = {
        delimiters: ['[[', ']]'],
        props: ['t'],
        template: '#transaction-item-template'
    };

    Transactions = {
        delimiters: ['[[', ']]'],
        components: {'transaction-item': TransactionItem},
        props: ['transactions'],
        template: '#transactions-template'
    };

    Stats = {
        delimiters: ['[[', ']]'],
        props: ['stats', 'price'],
        template: '#statistics-template'
    };

    new Vue({
        el: '#wallet',
        delimiters: ['[[', ']]'],
        components: {
            'stats': Stats,
            'transactions': Transactions
        },
        data: {
            message: '',
            loading: false,
            price : {
                usd: 1.0,
                percent_change_24h: "---"
            },
            stats : {
                hashes: 0,
                hashrate: '---',
                paid: 0,
                balance: 0,
                lastShare: '---'
            },
            transactions: []
        },
        created: function() {
            this.refreshWallet();
        },
        methods: {
            refreshWallet: refresh_wallet
        }
    });

});
