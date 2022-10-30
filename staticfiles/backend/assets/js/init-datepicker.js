(function($) {

    'use strict';

    $(document).ready(function() {

        $('.js-datepicker').datepicker({
            autoclose: true,
            allowClear: true
        });

        $('.input-group.date').datepicker({
            autoclose: true,
            todayHighlight: true,
            allowClear: true,
            daysOfWeekDisabled: [0,6]

        });

        $('.input-daterange').datepicker({
            autoclose: true,
            allowClear: true
        });

    });

})(window.jQuery);
