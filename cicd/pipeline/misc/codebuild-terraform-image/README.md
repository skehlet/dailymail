# README

Since the CodeBuild stages that run terraform plan and apply commands run inside our VPCs, they don't have internet access. This is a problem because terraform likes to download all its providers dynamically at runtime. So we have to build our own image with everything needed ahead of time.

TODO: find a more dynamic way to do it, keep it up to date, etc. For example:

* Find a well maintained image available on gallery.ecr.aws that includes `terraform`, and the terraform providers we need, as well as the `aws` command.
* Build it as part of this pipeline
* Set this up as a separate pipeline that periodically builds it and makes it available

But for now, just do this on your dev box.

```bash
aws ecr create-repository --repository-name codebuild-terraform-image
aws ecr put-lifecycle-policy \
    --repository-name codebuild-terraform-image \
    --lifecycle-policy-text "file://ecr-lifecycle-policy-keep-n-images.json"
```

Then grab all the providers:

```bash
rm -rf tf-plugins

cd ../../../app/terraform

terraform providers mirror \
    -platform=linux_amd64 \
    ../../pipeline/misc/codebuild-terraform-image/tf-plugins

cd ../../pipeline/misc/codebuild-terraform-image
```

Then docker build and push:

```bash
./build-and-push-to-ecr.sh
```
