(function($) {

    'use strict';

    $(document).ready(function() {

        $('#timepicker1').timepicker();

        $('#timepicker2').timepicker({
            autoclose: true,
            minuteStep: 1,
            showSeconds: false,
            showMeridian: false,
            useCurrent:false
        });

    });

})(window.jQuery);
