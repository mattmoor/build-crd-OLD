package(default_visibility = ["//visibility:public"])

load("@buildoid_pip//:requirements.bzl", "requirement")
load("@io_bazel_rules_docker//python:image.bzl", "py_image")

py_image(
    name = "build-controller",
    srcs = ["build-controller.py"],
    main = "build-controller.py",
    deps = [
        requirement("kubernetes"),
        requirement("google-api-python-client"),
    ],
)

load("@k8s_crd//:defaults.bzl", "k8s_crd")

k8s_crd(
    name = "build-crd",
    template = ":build.yaml",
)

load("@k8s_deployment//:defaults.bzl", "k8s_deployment")

k8s_deployment(
    name = "controller-deployment",
    images = {
        "us.gcr.io/convoy-adapter/build-controller:staging": ":build-controller",
    },
    template = ":build-controller.yaml",
)

load("@io_bazel_rules_k8s//k8s:objects.bzl", "k8s_objects")

k8s_objects(
    name = "everything",
    objects = [
        ":build-crd",
        ":controller-deployment",
    ],
)

load("@k8s_object//:defaults.bzl", "k8s_object")

k8s_object(
    name = "example-build-crd",
    template = ":example-build.yaml",
)
