function changeChartTimeWindow(chartData, timeWindow) {
    $.getJSON('data/'.concat(timeWindow), function (data) {
        chartData.labels = data.labels
        // chartData.datasets[0].data = data.datasets[0].data
        for (i = 0; i < chartData.datasets.length; i++) {
            chartData.datasets[i].data = data.datasets[i].data
        }
        window.temperatureChart.update(0);
    })
}

MODE = 'online'

var chartData = {
    labels: [],
    datasets: [{
        data: [],
        label: 'Air',
        pointRadius: 0,
        backgroundColor: 'rgba(0, 0, 0, 0)',
        borderColor: 'rgba(0, 255, 255, .8)'
    }, {
        data: [],
        label: 'Water: #1',
        pointRadius: 0,
        backgroundColor: 'rgba(0, 0, 0, 0)',
        borderColor: 'rgba(0, 128, 255, .8)'
    }, {
        data: [],
        label: 'Water: #2',
        pointRadius: 0,
        backgroundColor: 'rgba(0, 0, 0, 0)',
        borderColor: 'rgba(0, 255, 128, .8)'
    }]
}

$(document).ready(function () {
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // ping
    var ping_pong_times = [];
    var start_time;
    window.setInterval(function () {
        start_time = (new Date).getTime();
        socket.emit('my_ping');
    }, 1000);

    // pong
    socket.on('my_pong', function () {
        var latency = (new Date).getTime() - start_time;
        ping_pong_times.push(latency);
        ping_pong_times = ping_pong_times.slice(-30); // keep last 30 samples
        var sum = 0;
        for (var i = 0; i < ping_pong_times.length; i++)
            sum += ping_pong_times[i];
        $('#ping-pong').text(Math.round(10 * sum / ping_pong_times.length) / 10);
    });

    socket.on('uptime', function (msg) {
        $('#running_time').text(msg)
    });

    var ctx = document.getElementById("chart").getContext("2d");
    window.temperatureChart = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            legend: {
                display: true
            },
            scales: {
                xAxes: [{
                    type: 'time',
                    time: {
                        displayFormats: {
                            second: "HH:mm:ss",
                            minute: "HH:mm",
                            hour: "ddd, HH:mm",
                            day: " MMM Do"
                        }
                    },
                    ticks: {
                        fontColor: 'rgba(0, 255, 255, .4)'
                    },
                    gridLines: {
                        color: 'rgba(0, 255, 255, .2)'
                    }
                }],
                yAxes: [{
                    ticks: {
                        fontColor: 'rgba(0, 255, 255, .4)'

                    },
                    gridLines: {
                        color: 'rgba(0, 255, 255, .2)'
                    },
                    beforeBuildTicks: function (scale) {
                        data = scale.chart.config.data.datasets[0].data.filter(function (val) {
                            return val !== null
                        });
                        maxValue = Math.max(...data)
                        minValue = Math.min(...data)

                        scale.max = Math.ceil(maxValue + 1.5)

                        if (Math.abs(minValue) < 0.1) {
                            scale.min = 0
                        } else {
                            scale.min = Math.max(0, Math.floor(minValue - 1.5))
                        }
                    }
                }]
            },
            elements: {
                line: {
                    tension: .2
                }
            },
            animation: {
                easing: 'linear',
                duration: 1000
            },
            maintainAspectRatio: false,
            tooltips: {
                enabled: false
            },
            annotation: {
                annotations: [{
                    drawTime: "beforeDatasetsDraw",
                    type: "box",
                    yMin: 18.33,
                    yMax: 23.88,
                    yScaleID: "y-axis-0",
                    backgroundColor: 'rgba(0, 255, 128, .1)',
                    borderColor: 'rgba(0, 0, 0, 0)'
                }]
            }
        }
    });

    socket.on('temperature_measure', function (measurment) {
        // update text values and chart
        $('#temperature_value').text(measurment.temperature)
        $('#temperature_datetime').text(measurment.datetime)

        if (MODE == 'online') {
            // chartData.datasets[0].data.shift()                    
            // chartData.datasets[0].data.push(parseFloat(measurment.temperature))
            chartData.labels.shift()
            chartData.labels.push(measurment.datetime)

            chartData.datasets.forEach((dataset) => {
                dataset.data.shift();
            });
            chartData.datasets[0].data.push(parseFloat(measurment.temperature))

            window.temperatureChart.update()
        };
    });

});

function createButtonGroup(timeHorizontList, mode) {
    timeHorizontList.forEach(function (timeHorizont) {
        button = $('<a type="button" class="btn btn-default" id="btn_' + timeHorizont + '">' + timeHorizont + '</a>')

        button.click(function () {
            MODE = mode
            changeChartTimeWindow(chartData, '-' + timeHorizont)

            $('a', $('#btn_time_group')).removeClass('active')

            $(this).addClass('active')
        });

        $('#btn_time_group').append(button)
    })
}

// createButtonGroup(['5min'], 'online')
createButtonGroup(['20min', '1h', '8h', '24h', '48h', '1w', '2w', '4w'], 'offline')

changeChartTimeWindow(chartData, '-20min')
$('#btn_20min').addClass('active')
