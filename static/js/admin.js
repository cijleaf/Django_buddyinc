$(document).ready(function () {

    $("#modalButton").on("click", function () {
        $("#csaModal").show();
    });

    $("#csaModal .close").on("click", function () {
        $("#csaModal").hide();
    });

    $(".cancel-trans-frm").on("submit", function () {
        return confirm("Do you really want to cancel?")
    });
});

$(document).click(function(e) {

    if (e.target.id === "csaModal") {
        $("#csaModal").hide();
    }
});
