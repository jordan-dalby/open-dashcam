#include <iostream>
#include <thread>
#include <spdlog/spdlog.h>
#include <spdlog/sinks/rotating_file_sink.h>
#include "model.h"
#include "presenter.h"
#include "view.h"

void setup_logging() {
    auto console_sink = std::make_shared<spdlog::sinks::stdout_color_sink_mt>();
    auto file_sink = std::make_shared<spdlog::sinks::rotating_file_sink_mt>("dashcam.log", 1024 * 1024, 5);

    auto logger = std::make_shared<spdlog::logger>("dashcam", std::initializer_list<spdlog::sink_ptr>{console_sink, file_sink});
    logger->set_level(spdlog::level::debug);
    logger->flush_on(spdlog::level::debug);

    spdlog::set_default_logger(logger);
}

int main() {
    setup_logging();
    spdlog::debug("Logging initialized");

    DashCamModel model;
    DashCamPresenter presenter(model);
    DashCamView view(presenter);

    spdlog::info("Starting HTTP server");
    view.run("0.0.0.0", 5000);

    return 0;
}