/*
@author Ronan Delacroix
*/


$(document).ready(function() {


    function graph_transaction(transactions_graph_x_dates, transactions_graph_y_values) {
        var last_val = 0;
        var transactions_graph_y_stacked_values = _.map(transactions_graph_y_values, function (val) {
            last_val = last_val + val;
            return last_val;
        });
        var transactions_trace1 = {
            x: transactions_graph_x_dates,
            y: transactions_graph_y_stacked_values,
            name: 'Balance over time (ETN)',
            fill: 'tonexty',
            type: 'scatter'
        };

        var marker_size_factor = 30/_.max(transactions_graph_y_values);
        var transaction_trace2 = {
            x: transactions_graph_x_dates,
            y: transactions_graph_y_values,
            marker: {
                color: 'rgb(188, 208, 220)',
                size: _.map(transactions_graph_y_values, function (d) {return d*marker_size_factor;}),
            },
            name: 'Payments (ETN)',
            yaxis: 'y2',
            mode: 'markers',
            type: 'scatter'
        };
        var layout = {
            title: 'Mining pool Payments',
	        legend: {
                orientation: "h",
                x: 0.35
            },
            margin: {
                t: 50,
                b: 10
            },
            yaxis: {
                title: 'Overall Balance (ETN)',
                hoverformat: '.1f',
                ticksuffix: ' ETN'
            },
            yaxis2: {
                title: 'Payments (ETN)',
                titlefont: {color: 'rgb(188, 208, 220)'},
                tickfont: {color: 'rgb(188, 208, 220)'},
                hoverformat: '.1f',
                ticksuffix: ' ETN',
                overlaying: 'y',
                rangemode:'tozero',
                side: 'right'
            }
        };
        Plotly.newPlot('transactions_graph', [transactions_trace1, transaction_trace2], layout);
    }

    function graph_hash(data) {
        var dates = _.map(data, _.first);
        dates = _.map(dates, function(d) {return moment(d * 1000).toISOString();});
        var rate = _.map(data, function(d) {return d[1];});
        var hash_trace = {
            x: dates,
            y: rate,
            name: 'Balance over time (ETN)',
            fill: 'tonexty',
            type: 'scatter'
        };
        var layout = {
            title: 'Mining pool Hash Rate',
            yaxis: {
                title: 'Hashrate (H/s)',
                ticksuffix: ' H/s'
            },
            showlegend: false
        };
        Plotly.newPlot('hash_graph', [hash_trace], layout);
    }

    function graph_payment(data) {
        var dates = _.map(data, _.first);
        dates = _.map(dates, function(d) {return moment(d * 1000).toISOString();});
        var rate = _.map(data, function(d) {return d[1];});
        var hash_trace = {
            x: dates,
            y: rate,
            name: 'Payments over time (ETN)',
            fill: 'tonexty',
            type: 'scatter'
        };
        var layout = {
            title: 'Payments',
            yaxis: {
                title: 'Value (ETN)',
                ticksuffix: ' ETN'
            },
            showlegend: false
        };
        Plotly.newPlot('payment_graph', [hash_trace], layout);
    }

    function process_stats(vm, data) {

        vm.stats = data.stats;
        vm.stats.lastShare = moment(vm.stats.lastShare*1000).calendar();

        var transactions_graph_x_dates = [];
        var transactions_graph_y_values = [];
        var transactions = [];
        var payments = data.payments;

        for (var i = 0; i < payments.length; i += 2) {
            var p = payments[i];
            var parts = p.split(':');
            var payment = {
                time: moment(payments[i + 1] * 1000).calendar(),
                hash: parts[0],
                amount: (parts[1] / 100.0).toFixed(2) + ' ETN',
                fee: (parts[2] / 100.0).toFixed(2) + ' ETN',
                mixin: parts[3]
            };
            transactions.push(payment);
            transactions_graph_x_dates.push(moment(payments[i + 1] * 1000).toISOString())
            transactions_graph_y_values.push(parts[1] / 100.0)
        }
        vm.transactions = transactions;
        vm.message = 'Wallet loaded';

        transactions_graph_x_dates = transactions_graph_x_dates.reverse();
        transactions_graph_y_values = transactions_graph_y_values.reverse();

        graph_transaction(transactions_graph_x_dates, transactions_graph_y_values);

        if (data.charts) {
            $('#hash_graph').removeClass('hidden');
            $('#payment_graph').removeClass('hidden');
            graph_hash(data.charts.hashrate);
            graph_payment(data.charts.payments);
        }
    }

    function refresh_wallet() {
        this.message = 'Loading...';
        this.loading = true;
        var vm = this;
        axios.get(WALLET_API_URL+'?address='+WALLET_ID).then(function (response) {
            process_stats(vm, response.data);
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
            vm.price.percent_change_7d = electroneum.percent_change_7d;
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
