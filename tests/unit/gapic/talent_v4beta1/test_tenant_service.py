# -*- coding: utf-8 -*-

# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import mock

import grpc
from grpc.experimental import aio
import math
import pytest
from proto.marshal.rules.dates import DurationRule, TimestampRule

from google import auth
from google.api_core import client_options
from google.api_core import exceptions
from google.api_core import gapic_v1
from google.api_core import grpc_helpers
from google.api_core import grpc_helpers_async
from google.auth import credentials
from google.auth.exceptions import MutualTLSChannelError
from google.cloud.talent_v4beta1.services.tenant_service import TenantServiceAsyncClient
from google.cloud.talent_v4beta1.services.tenant_service import TenantServiceClient
from google.cloud.talent_v4beta1.services.tenant_service import pagers
from google.cloud.talent_v4beta1.services.tenant_service import transports
from google.cloud.talent_v4beta1.types import tenant
from google.cloud.talent_v4beta1.types import tenant as gct_tenant
from google.cloud.talent_v4beta1.types import tenant_service
from google.oauth2 import service_account
from google.protobuf import field_mask_pb2 as field_mask  # type: ignore


def client_cert_source_callback():
    return b"cert bytes", b"key bytes"


# If default endpoint is localhost, then default mtls endpoint will be the same.
# This method modifies the default endpoint so the client can produce a different
# mtls endpoint for endpoint testing purposes.
def modify_default_endpoint(client):
    return (
        "foo.googleapis.com"
        if ("localhost" in client.DEFAULT_ENDPOINT)
        else client.DEFAULT_ENDPOINT
    )


def test__get_default_mtls_endpoint():
    api_endpoint = "example.googleapis.com"
    api_mtls_endpoint = "example.mtls.googleapis.com"
    sandbox_endpoint = "example.sandbox.googleapis.com"
    sandbox_mtls_endpoint = "example.mtls.sandbox.googleapis.com"
    non_googleapi = "api.example.com"

    assert TenantServiceClient._get_default_mtls_endpoint(None) is None
    assert (
        TenantServiceClient._get_default_mtls_endpoint(api_endpoint)
        == api_mtls_endpoint
    )
    assert (
        TenantServiceClient._get_default_mtls_endpoint(api_mtls_endpoint)
        == api_mtls_endpoint
    )
    assert (
        TenantServiceClient._get_default_mtls_endpoint(sandbox_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        TenantServiceClient._get_default_mtls_endpoint(sandbox_mtls_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        TenantServiceClient._get_default_mtls_endpoint(non_googleapi) == non_googleapi
    )


@pytest.mark.parametrize(
    "client_class", [TenantServiceClient, TenantServiceAsyncClient]
)
def test_tenant_service_client_from_service_account_file(client_class):
    creds = credentials.AnonymousCredentials()
    with mock.patch.object(
        service_account.Credentials, "from_service_account_file"
    ) as factory:
        factory.return_value = creds
        client = client_class.from_service_account_file("dummy/file/path.json")
        assert client._transport._credentials == creds

        client = client_class.from_service_account_json("dummy/file/path.json")
        assert client._transport._credentials == creds

        assert client._transport._host == "jobs.googleapis.com:443"


def test_tenant_service_client_get_transport_class():
    transport = TenantServiceClient.get_transport_class()
    assert transport == transports.TenantServiceGrpcTransport

    transport = TenantServiceClient.get_transport_class("grpc")
    assert transport == transports.TenantServiceGrpcTransport


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (TenantServiceClient, transports.TenantServiceGrpcTransport, "grpc"),
        (
            TenantServiceAsyncClient,
            transports.TenantServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
@mock.patch.object(
    TenantServiceClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(TenantServiceClient),
)
@mock.patch.object(
    TenantServiceAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(TenantServiceAsyncClient),
)
def test_tenant_service_client_client_options(
    client_class, transport_class, transport_name
):
    # Check that if channel is provided we won't create a new one.
    with mock.patch.object(TenantServiceClient, "get_transport_class") as gtc:
        transport = transport_class(credentials=credentials.AnonymousCredentials())
        client = client_class(transport=transport)
        gtc.assert_not_called()

    # Check that if channel is provided via str we will create a new one.
    with mock.patch.object(TenantServiceClient, "get_transport_class") as gtc:
        client = client_class(transport=transport_name)
        gtc.assert_called()

    # Check the case api_endpoint is provided.
    options = client_options.ClientOptions(api_endpoint="squid.clam.whelk")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            api_mtls_endpoint="squid.clam.whelk",
            client_cert_source=None,
            quota_project_id=None,
        )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS is
    # "never".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS": "never"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class()
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_ENDPOINT,
                scopes=None,
                api_mtls_endpoint=client.DEFAULT_ENDPOINT,
                client_cert_source=None,
                quota_project_id=None,
            )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS is
    # "always".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS": "always"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class()
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_MTLS_ENDPOINT,
                scopes=None,
                api_mtls_endpoint=client.DEFAULT_MTLS_ENDPOINT,
                client_cert_source=None,
                quota_project_id=None,
            )

    # Check the case api_endpoint is not provided, GOOGLE_API_USE_MTLS is
    # "auto", and client_cert_source is provided.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS": "auto"}):
        options = client_options.ClientOptions(
            client_cert_source=client_cert_source_callback
        )
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class(client_options=options)
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_MTLS_ENDPOINT,
                scopes=None,
                api_mtls_endpoint=client.DEFAULT_MTLS_ENDPOINT,
                client_cert_source=client_cert_source_callback,
                quota_project_id=None,
            )

    # Check the case api_endpoint is not provided, GOOGLE_API_USE_MTLS is
    # "auto", and default_client_cert_source is provided.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS": "auto"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            with mock.patch(
                "google.auth.transport.mtls.has_default_client_cert_source",
                return_value=True,
            ):
                patched.return_value = None
                client = client_class()
                patched.assert_called_once_with(
                    credentials=None,
                    credentials_file=None,
                    host=client.DEFAULT_MTLS_ENDPOINT,
                    scopes=None,
                    api_mtls_endpoint=client.DEFAULT_MTLS_ENDPOINT,
                    client_cert_source=None,
                    quota_project_id=None,
                )

    # Check the case api_endpoint is not provided, GOOGLE_API_USE_MTLS is
    # "auto", but client_cert_source and default_client_cert_source are None.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS": "auto"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            with mock.patch(
                "google.auth.transport.mtls.has_default_client_cert_source",
                return_value=False,
            ):
                patched.return_value = None
                client = client_class()
                patched.assert_called_once_with(
                    credentials=None,
                    credentials_file=None,
                    host=client.DEFAULT_ENDPOINT,
                    scopes=None,
                    api_mtls_endpoint=client.DEFAULT_ENDPOINT,
                    client_cert_source=None,
                    quota_project_id=None,
                )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS has
    # unsupported value.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS": "Unsupported"}):
        with pytest.raises(MutualTLSChannelError):
            client = client_class()

    # Check the case quota_project_id is provided
    options = client_options.ClientOptions(quota_project_id="octopus")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            api_mtls_endpoint=client.DEFAULT_ENDPOINT,
            client_cert_source=None,
            quota_project_id="octopus",
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (TenantServiceClient, transports.TenantServiceGrpcTransport, "grpc"),
        (
            TenantServiceAsyncClient,
            transports.TenantServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_tenant_service_client_client_options_scopes(
    client_class, transport_class, transport_name
):
    # Check the case scopes are provided.
    options = client_options.ClientOptions(scopes=["1", "2"],)
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=["1", "2"],
            api_mtls_endpoint=client.DEFAULT_ENDPOINT,
            client_cert_source=None,
            quota_project_id=None,
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (TenantServiceClient, transports.TenantServiceGrpcTransport, "grpc"),
        (
            TenantServiceAsyncClient,
            transports.TenantServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_tenant_service_client_client_options_credentials_file(
    client_class, transport_class, transport_name
):
    # Check the case credentials file is provided.
    options = client_options.ClientOptions(credentials_file="credentials.json")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file="credentials.json",
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            api_mtls_endpoint=client.DEFAULT_ENDPOINT,
            client_cert_source=None,
            quota_project_id=None,
        )


def test_tenant_service_client_client_options_from_dict():
    with mock.patch(
        "google.cloud.talent_v4beta1.services.tenant_service.transports.TenantServiceGrpcTransport.__init__"
    ) as grpc_transport:
        grpc_transport.return_value = None
        client = TenantServiceClient(
            client_options={"api_endpoint": "squid.clam.whelk"}
        )
        grpc_transport.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            api_mtls_endpoint="squid.clam.whelk",
            client_cert_source=None,
            quota_project_id=None,
        )


def test_create_tenant(
    transport: str = "grpc", request_type=tenant_service.CreateTenantRequest
):
    client = TenantServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.create_tenant), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gct_tenant.Tenant(
            name="name_value",
            external_id="external_id_value",
            usage_type=gct_tenant.Tenant.DataUsageType.AGGREGATED,
            keyword_searchable_profile_custom_attributes=[
                "keyword_searchable_profile_custom_attributes_value"
            ],
        )

        response = client.create_tenant(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == tenant_service.CreateTenantRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gct_tenant.Tenant)

    assert response.name == "name_value"

    assert response.external_id == "external_id_value"

    assert response.usage_type == gct_tenant.Tenant.DataUsageType.AGGREGATED

    assert response.keyword_searchable_profile_custom_attributes == [
        "keyword_searchable_profile_custom_attributes_value"
    ]


def test_create_tenant_from_dict():
    test_create_tenant(request_type=dict)


@pytest.mark.asyncio
async def test_create_tenant_async(transport: str = "grpc_asyncio"):
    client = TenantServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = tenant_service.CreateTenantRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_tenant), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gct_tenant.Tenant(
                name="name_value",
                external_id="external_id_value",
                usage_type=gct_tenant.Tenant.DataUsageType.AGGREGATED,
                keyword_searchable_profile_custom_attributes=[
                    "keyword_searchable_profile_custom_attributes_value"
                ],
            )
        )

        response = await client.create_tenant(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gct_tenant.Tenant)

    assert response.name == "name_value"

    assert response.external_id == "external_id_value"

    assert response.usage_type == gct_tenant.Tenant.DataUsageType.AGGREGATED

    assert response.keyword_searchable_profile_custom_attributes == [
        "keyword_searchable_profile_custom_attributes_value"
    ]


def test_create_tenant_field_headers():
    client = TenantServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tenant_service.CreateTenantRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.create_tenant), "__call__") as call:
        call.return_value = gct_tenant.Tenant()

        client.create_tenant(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_tenant_field_headers_async():
    client = TenantServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tenant_service.CreateTenantRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_tenant), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gct_tenant.Tenant())

        await client.create_tenant(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_create_tenant_flattened():
    client = TenantServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.create_tenant), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gct_tenant.Tenant()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_tenant(
            parent="parent_value", tenant=gct_tenant.Tenant(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].tenant == gct_tenant.Tenant(name="name_value")


def test_create_tenant_flattened_error():
    client = TenantServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_tenant(
            tenant_service.CreateTenantRequest(),
            parent="parent_value",
            tenant=gct_tenant.Tenant(name="name_value"),
        )


@pytest.mark.asyncio
async def test_create_tenant_flattened_async():
    client = TenantServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_tenant), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gct_tenant.Tenant()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gct_tenant.Tenant())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_tenant(
            parent="parent_value", tenant=gct_tenant.Tenant(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].tenant == gct_tenant.Tenant(name="name_value")


@pytest.mark.asyncio
async def test_create_tenant_flattened_error_async():
    client = TenantServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_tenant(
            tenant_service.CreateTenantRequest(),
            parent="parent_value",
            tenant=gct_tenant.Tenant(name="name_value"),
        )


def test_get_tenant(
    transport: str = "grpc", request_type=tenant_service.GetTenantRequest
):
    client = TenantServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_tenant), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = tenant.Tenant(
            name="name_value",
            external_id="external_id_value",
            usage_type=tenant.Tenant.DataUsageType.AGGREGATED,
            keyword_searchable_profile_custom_attributes=[
                "keyword_searchable_profile_custom_attributes_value"
            ],
        )

        response = client.get_tenant(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == tenant_service.GetTenantRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, tenant.Tenant)

    assert response.name == "name_value"

    assert response.external_id == "external_id_value"

    assert response.usage_type == tenant.Tenant.DataUsageType.AGGREGATED

    assert response.keyword_searchable_profile_custom_attributes == [
        "keyword_searchable_profile_custom_attributes_value"
    ]


def test_get_tenant_from_dict():
    test_get_tenant(request_type=dict)


@pytest.mark.asyncio
async def test_get_tenant_async(transport: str = "grpc_asyncio"):
    client = TenantServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = tenant_service.GetTenantRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_tenant), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tenant.Tenant(
                name="name_value",
                external_id="external_id_value",
                usage_type=tenant.Tenant.DataUsageType.AGGREGATED,
                keyword_searchable_profile_custom_attributes=[
                    "keyword_searchable_profile_custom_attributes_value"
                ],
            )
        )

        response = await client.get_tenant(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, tenant.Tenant)

    assert response.name == "name_value"

    assert response.external_id == "external_id_value"

    assert response.usage_type == tenant.Tenant.DataUsageType.AGGREGATED

    assert response.keyword_searchable_profile_custom_attributes == [
        "keyword_searchable_profile_custom_attributes_value"
    ]


def test_get_tenant_field_headers():
    client = TenantServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tenant_service.GetTenantRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_tenant), "__call__") as call:
        call.return_value = tenant.Tenant()

        client.get_tenant(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_tenant_field_headers_async():
    client = TenantServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tenant_service.GetTenantRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_tenant), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(tenant.Tenant())

        await client.get_tenant(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_tenant_flattened():
    client = TenantServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_tenant), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = tenant.Tenant()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_tenant(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_get_tenant_flattened_error():
    client = TenantServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_tenant(
            tenant_service.GetTenantRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_tenant_flattened_async():
    client = TenantServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_tenant), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tenant.Tenant()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(tenant.Tenant())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_tenant(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_tenant_flattened_error_async():
    client = TenantServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_tenant(
            tenant_service.GetTenantRequest(), name="name_value",
        )


def test_update_tenant(
    transport: str = "grpc", request_type=tenant_service.UpdateTenantRequest
):
    client = TenantServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.update_tenant), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gct_tenant.Tenant(
            name="name_value",
            external_id="external_id_value",
            usage_type=gct_tenant.Tenant.DataUsageType.AGGREGATED,
            keyword_searchable_profile_custom_attributes=[
                "keyword_searchable_profile_custom_attributes_value"
            ],
        )

        response = client.update_tenant(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == tenant_service.UpdateTenantRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gct_tenant.Tenant)

    assert response.name == "name_value"

    assert response.external_id == "external_id_value"

    assert response.usage_type == gct_tenant.Tenant.DataUsageType.AGGREGATED

    assert response.keyword_searchable_profile_custom_attributes == [
        "keyword_searchable_profile_custom_attributes_value"
    ]


def test_update_tenant_from_dict():
    test_update_tenant(request_type=dict)


@pytest.mark.asyncio
async def test_update_tenant_async(transport: str = "grpc_asyncio"):
    client = TenantServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = tenant_service.UpdateTenantRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_tenant), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gct_tenant.Tenant(
                name="name_value",
                external_id="external_id_value",
                usage_type=gct_tenant.Tenant.DataUsageType.AGGREGATED,
                keyword_searchable_profile_custom_attributes=[
                    "keyword_searchable_profile_custom_attributes_value"
                ],
            )
        )

        response = await client.update_tenant(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gct_tenant.Tenant)

    assert response.name == "name_value"

    assert response.external_id == "external_id_value"

    assert response.usage_type == gct_tenant.Tenant.DataUsageType.AGGREGATED

    assert response.keyword_searchable_profile_custom_attributes == [
        "keyword_searchable_profile_custom_attributes_value"
    ]


def test_update_tenant_field_headers():
    client = TenantServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tenant_service.UpdateTenantRequest()
    request.tenant.name = "tenant.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.update_tenant), "__call__") as call:
        call.return_value = gct_tenant.Tenant()

        client.update_tenant(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "tenant.name=tenant.name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_update_tenant_field_headers_async():
    client = TenantServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tenant_service.UpdateTenantRequest()
    request.tenant.name = "tenant.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_tenant), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gct_tenant.Tenant())

        await client.update_tenant(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "tenant.name=tenant.name/value",) in kw["metadata"]


def test_update_tenant_flattened():
    client = TenantServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.update_tenant), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gct_tenant.Tenant()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_tenant(tenant=gct_tenant.Tenant(name="name_value"),)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].tenant == gct_tenant.Tenant(name="name_value")


def test_update_tenant_flattened_error():
    client = TenantServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_tenant(
            tenant_service.UpdateTenantRequest(),
            tenant=gct_tenant.Tenant(name="name_value"),
        )


@pytest.mark.asyncio
async def test_update_tenant_flattened_async():
    client = TenantServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_tenant), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gct_tenant.Tenant()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gct_tenant.Tenant())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_tenant(
            tenant=gct_tenant.Tenant(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].tenant == gct_tenant.Tenant(name="name_value")


@pytest.mark.asyncio
async def test_update_tenant_flattened_error_async():
    client = TenantServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_tenant(
            tenant_service.UpdateTenantRequest(),
            tenant=gct_tenant.Tenant(name="name_value"),
        )


def test_delete_tenant(
    transport: str = "grpc", request_type=tenant_service.DeleteTenantRequest
):
    client = TenantServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.delete_tenant), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        response = client.delete_tenant(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == tenant_service.DeleteTenantRequest()

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_tenant_from_dict():
    test_delete_tenant(request_type=dict)


@pytest.mark.asyncio
async def test_delete_tenant_async(transport: str = "grpc_asyncio"):
    client = TenantServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = tenant_service.DeleteTenantRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_tenant), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        response = await client.delete_tenant(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_tenant_field_headers():
    client = TenantServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tenant_service.DeleteTenantRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.delete_tenant), "__call__") as call:
        call.return_value = None

        client.delete_tenant(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_tenant_field_headers_async():
    client = TenantServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tenant_service.DeleteTenantRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_tenant), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        await client.delete_tenant(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_delete_tenant_flattened():
    client = TenantServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.delete_tenant), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_tenant(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_delete_tenant_flattened_error():
    client = TenantServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_tenant(
            tenant_service.DeleteTenantRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_tenant_flattened_async():
    client = TenantServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_tenant), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_tenant(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_delete_tenant_flattened_error_async():
    client = TenantServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_tenant(
            tenant_service.DeleteTenantRequest(), name="name_value",
        )


def test_list_tenants(
    transport: str = "grpc", request_type=tenant_service.ListTenantsRequest
):
    client = TenantServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_tenants), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = tenant_service.ListTenantsResponse(
            next_page_token="next_page_token_value",
        )

        response = client.list_tenants(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == tenant_service.ListTenantsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListTenantsPager)

    assert response.next_page_token == "next_page_token_value"


def test_list_tenants_from_dict():
    test_list_tenants(request_type=dict)


@pytest.mark.asyncio
async def test_list_tenants_async(transport: str = "grpc_asyncio"):
    client = TenantServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = tenant_service.ListTenantsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_tenants), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tenant_service.ListTenantsResponse(next_page_token="next_page_token_value",)
        )

        response = await client.list_tenants(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListTenantsAsyncPager)

    assert response.next_page_token == "next_page_token_value"


def test_list_tenants_field_headers():
    client = TenantServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tenant_service.ListTenantsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_tenants), "__call__") as call:
        call.return_value = tenant_service.ListTenantsResponse()

        client.list_tenants(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_tenants_field_headers_async():
    client = TenantServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tenant_service.ListTenantsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_tenants), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tenant_service.ListTenantsResponse()
        )

        await client.list_tenants(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_tenants_flattened():
    client = TenantServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_tenants), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = tenant_service.ListTenantsResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_tenants(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"


def test_list_tenants_flattened_error():
    client = TenantServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_tenants(
            tenant_service.ListTenantsRequest(), parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_tenants_flattened_async():
    client = TenantServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_tenants), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tenant_service.ListTenantsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tenant_service.ListTenantsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_tenants(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_list_tenants_flattened_error_async():
    client = TenantServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_tenants(
            tenant_service.ListTenantsRequest(), parent="parent_value",
        )


def test_list_tenants_pager():
    client = TenantServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_tenants), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            tenant_service.ListTenantsResponse(
                tenants=[tenant.Tenant(), tenant.Tenant(), tenant.Tenant(),],
                next_page_token="abc",
            ),
            tenant_service.ListTenantsResponse(tenants=[], next_page_token="def",),
            tenant_service.ListTenantsResponse(
                tenants=[tenant.Tenant(),], next_page_token="ghi",
            ),
            tenant_service.ListTenantsResponse(
                tenants=[tenant.Tenant(), tenant.Tenant(),],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_tenants(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, tenant.Tenant) for i in results)


def test_list_tenants_pages():
    client = TenantServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_tenants), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            tenant_service.ListTenantsResponse(
                tenants=[tenant.Tenant(), tenant.Tenant(), tenant.Tenant(),],
                next_page_token="abc",
            ),
            tenant_service.ListTenantsResponse(tenants=[], next_page_token="def",),
            tenant_service.ListTenantsResponse(
                tenants=[tenant.Tenant(),], next_page_token="ghi",
            ),
            tenant_service.ListTenantsResponse(
                tenants=[tenant.Tenant(), tenant.Tenant(),],
            ),
            RuntimeError,
        )
        pages = list(client.list_tenants(request={}).pages)
        for page, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_tenants_async_pager():
    client = TenantServiceAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_tenants),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            tenant_service.ListTenantsResponse(
                tenants=[tenant.Tenant(), tenant.Tenant(), tenant.Tenant(),],
                next_page_token="abc",
            ),
            tenant_service.ListTenantsResponse(tenants=[], next_page_token="def",),
            tenant_service.ListTenantsResponse(
                tenants=[tenant.Tenant(),], next_page_token="ghi",
            ),
            tenant_service.ListTenantsResponse(
                tenants=[tenant.Tenant(), tenant.Tenant(),],
            ),
            RuntimeError,
        )
        async_pager = await client.list_tenants(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, tenant.Tenant) for i in responses)


@pytest.mark.asyncio
async def test_list_tenants_async_pages():
    client = TenantServiceAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_tenants),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            tenant_service.ListTenantsResponse(
                tenants=[tenant.Tenant(), tenant.Tenant(), tenant.Tenant(),],
                next_page_token="abc",
            ),
            tenant_service.ListTenantsResponse(tenants=[], next_page_token="def",),
            tenant_service.ListTenantsResponse(
                tenants=[tenant.Tenant(),], next_page_token="ghi",
            ),
            tenant_service.ListTenantsResponse(
                tenants=[tenant.Tenant(), tenant.Tenant(),],
            ),
            RuntimeError,
        )
        pages = []
        async for page in (await client.list_tenants(request={})).pages:
            pages.append(page)
        for page, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page.raw_page.next_page_token == token


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.TenantServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = TenantServiceClient(
            credentials=credentials.AnonymousCredentials(), transport=transport,
        )

    # It is an error to provide a credentials file and a transport instance.
    transport = transports.TenantServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = TenantServiceClient(
            client_options={"credentials_file": "credentials.json"},
            transport=transport,
        )

    # It is an error to provide scopes and a transport instance.
    transport = transports.TenantServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = TenantServiceClient(
            client_options={"scopes": ["1", "2"]}, transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.TenantServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    client = TenantServiceClient(transport=transport)
    assert client._transport is transport


def test_transport_get_channel():
    # A client may be instantiated with a custom transport instance.
    transport = transports.TenantServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel

    transport = transports.TenantServiceGrpcAsyncIOTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel


def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = TenantServiceClient(credentials=credentials.AnonymousCredentials(),)
    assert isinstance(client._transport, transports.TenantServiceGrpcTransport,)


def test_tenant_service_base_transport_error():
    # Passing both a credentials object and credentials_file should raise an error
    with pytest.raises(exceptions.DuplicateCredentialArgs):
        transport = transports.TenantServiceTransport(
            credentials=credentials.AnonymousCredentials(),
            credentials_file="credentials.json",
        )


def test_tenant_service_base_transport():
    # Instantiate the base transport.
    with mock.patch(
        "google.cloud.talent_v4beta1.services.tenant_service.transports.TenantServiceTransport.__init__"
    ) as Transport:
        Transport.return_value = None
        transport = transports.TenantServiceTransport(
            credentials=credentials.AnonymousCredentials(),
        )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        "create_tenant",
        "get_tenant",
        "update_tenant",
        "delete_tenant",
        "list_tenants",
    )
    for method in methods:
        with pytest.raises(NotImplementedError):
            getattr(transport, method)(request=object())


def test_tenant_service_base_transport_with_credentials_file():
    # Instantiate the base transport with a credentials file
    with mock.patch.object(
        auth, "load_credentials_from_file"
    ) as load_creds, mock.patch(
        "google.cloud.talent_v4beta1.services.tenant_service.transports.TenantServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        load_creds.return_value = (credentials.AnonymousCredentials(), None)
        transport = transports.TenantServiceTransport(
            credentials_file="credentials.json", quota_project_id="octopus",
        )
        load_creds.assert_called_once_with(
            "credentials.json",
            scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/jobs",
            ),
            quota_project_id="octopus",
        )


def test_tenant_service_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        TenantServiceClient()
        adc.assert_called_once_with(
            scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/jobs",
            ),
            quota_project_id=None,
        )


def test_tenant_service_transport_auth_adc():
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        transports.TenantServiceGrpcTransport(
            host="squid.clam.whelk", quota_project_id="octopus"
        )
        adc.assert_called_once_with(
            scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/jobs",
            ),
            quota_project_id="octopus",
        )


def test_tenant_service_host_no_port():
    client = TenantServiceClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(api_endpoint="jobs.googleapis.com"),
    )
    assert client._transport._host == "jobs.googleapis.com:443"


def test_tenant_service_host_with_port():
    client = TenantServiceClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="jobs.googleapis.com:8000"
        ),
    )
    assert client._transport._host == "jobs.googleapis.com:8000"


def test_tenant_service_grpc_transport_channel():
    channel = grpc.insecure_channel("http://localhost/")

    # Check that if channel is provided, mtls endpoint and client_cert_source
    # won't be used.
    callback = mock.MagicMock()
    transport = transports.TenantServiceGrpcTransport(
        host="squid.clam.whelk",
        channel=channel,
        api_mtls_endpoint="mtls.squid.clam.whelk",
        client_cert_source=callback,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert not callback.called


def test_tenant_service_grpc_asyncio_transport_channel():
    channel = aio.insecure_channel("http://localhost/")

    # Check that if channel is provided, mtls endpoint and client_cert_source
    # won't be used.
    callback = mock.MagicMock()
    transport = transports.TenantServiceGrpcAsyncIOTransport(
        host="squid.clam.whelk",
        channel=channel,
        api_mtls_endpoint="mtls.squid.clam.whelk",
        client_cert_source=callback,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert not callback.called


@mock.patch("grpc.ssl_channel_credentials", autospec=True)
@mock.patch("google.api_core.grpc_helpers.create_channel", autospec=True)
def test_tenant_service_grpc_transport_channel_mtls_with_client_cert_source(
    grpc_create_channel, grpc_ssl_channel_cred
):
    # Check that if channel is None, but api_mtls_endpoint and client_cert_source
    # are provided, then a mTLS channel will be created.
    mock_cred = mock.Mock()

    mock_ssl_cred = mock.Mock()
    grpc_ssl_channel_cred.return_value = mock_ssl_cred

    mock_grpc_channel = mock.Mock()
    grpc_create_channel.return_value = mock_grpc_channel

    transport = transports.TenantServiceGrpcTransport(
        host="squid.clam.whelk",
        credentials=mock_cred,
        api_mtls_endpoint="mtls.squid.clam.whelk",
        client_cert_source=client_cert_source_callback,
    )
    grpc_ssl_channel_cred.assert_called_once_with(
        certificate_chain=b"cert bytes", private_key=b"key bytes"
    )
    grpc_create_channel.assert_called_once_with(
        "mtls.squid.clam.whelk:443",
        credentials=mock_cred,
        credentials_file=None,
        scopes=(
            "https://www.googleapis.com/auth/cloud-platform",
            "https://www.googleapis.com/auth/jobs",
        ),
        ssl_credentials=mock_ssl_cred,
        quota_project_id=None,
    )
    assert transport.grpc_channel == mock_grpc_channel


@mock.patch("grpc.ssl_channel_credentials", autospec=True)
@mock.patch("google.api_core.grpc_helpers_async.create_channel", autospec=True)
def test_tenant_service_grpc_asyncio_transport_channel_mtls_with_client_cert_source(
    grpc_create_channel, grpc_ssl_channel_cred
):
    # Check that if channel is None, but api_mtls_endpoint and client_cert_source
    # are provided, then a mTLS channel will be created.
    mock_cred = mock.Mock()

    mock_ssl_cred = mock.Mock()
    grpc_ssl_channel_cred.return_value = mock_ssl_cred

    mock_grpc_channel = mock.Mock()
    grpc_create_channel.return_value = mock_grpc_channel

    transport = transports.TenantServiceGrpcAsyncIOTransport(
        host="squid.clam.whelk",
        credentials=mock_cred,
        api_mtls_endpoint="mtls.squid.clam.whelk",
        client_cert_source=client_cert_source_callback,
    )
    grpc_ssl_channel_cred.assert_called_once_with(
        certificate_chain=b"cert bytes", private_key=b"key bytes"
    )
    grpc_create_channel.assert_called_once_with(
        "mtls.squid.clam.whelk:443",
        credentials=mock_cred,
        credentials_file=None,
        scopes=(
            "https://www.googleapis.com/auth/cloud-platform",
            "https://www.googleapis.com/auth/jobs",
        ),
        ssl_credentials=mock_ssl_cred,
        quota_project_id=None,
    )
    assert transport.grpc_channel == mock_grpc_channel


@pytest.mark.parametrize(
    "api_mtls_endpoint", ["mtls.squid.clam.whelk", "mtls.squid.clam.whelk:443"]
)
@mock.patch("google.api_core.grpc_helpers.create_channel", autospec=True)
def test_tenant_service_grpc_transport_channel_mtls_with_adc(
    grpc_create_channel, api_mtls_endpoint
):
    # Check that if channel and client_cert_source are None, but api_mtls_endpoint
    # is provided, then a mTLS channel will be created with SSL ADC.
    mock_grpc_channel = mock.Mock()
    grpc_create_channel.return_value = mock_grpc_channel

    # Mock google.auth.transport.grpc.SslCredentials class.
    mock_ssl_cred = mock.Mock()
    with mock.patch.multiple(
        "google.auth.transport.grpc.SslCredentials",
        __init__=mock.Mock(return_value=None),
        ssl_credentials=mock.PropertyMock(return_value=mock_ssl_cred),
    ):
        mock_cred = mock.Mock()
        transport = transports.TenantServiceGrpcTransport(
            host="squid.clam.whelk",
            credentials=mock_cred,
            api_mtls_endpoint=api_mtls_endpoint,
            client_cert_source=None,
        )
        grpc_create_channel.assert_called_once_with(
            "mtls.squid.clam.whelk:443",
            credentials=mock_cred,
            credentials_file=None,
            scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/jobs",
            ),
            ssl_credentials=mock_ssl_cred,
            quota_project_id=None,
        )
        assert transport.grpc_channel == mock_grpc_channel


@pytest.mark.parametrize(
    "api_mtls_endpoint", ["mtls.squid.clam.whelk", "mtls.squid.clam.whelk:443"]
)
@mock.patch("google.api_core.grpc_helpers_async.create_channel", autospec=True)
def test_tenant_service_grpc_asyncio_transport_channel_mtls_with_adc(
    grpc_create_channel, api_mtls_endpoint
):
    # Check that if channel and client_cert_source are None, but api_mtls_endpoint
    # is provided, then a mTLS channel will be created with SSL ADC.
    mock_grpc_channel = mock.Mock()
    grpc_create_channel.return_value = mock_grpc_channel

    # Mock google.auth.transport.grpc.SslCredentials class.
    mock_ssl_cred = mock.Mock()
    with mock.patch.multiple(
        "google.auth.transport.grpc.SslCredentials",
        __init__=mock.Mock(return_value=None),
        ssl_credentials=mock.PropertyMock(return_value=mock_ssl_cred),
    ):
        mock_cred = mock.Mock()
        transport = transports.TenantServiceGrpcAsyncIOTransport(
            host="squid.clam.whelk",
            credentials=mock_cred,
            api_mtls_endpoint=api_mtls_endpoint,
            client_cert_source=None,
        )
        grpc_create_channel.assert_called_once_with(
            "mtls.squid.clam.whelk:443",
            credentials=mock_cred,
            credentials_file=None,
            scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/jobs",
            ),
            ssl_credentials=mock_ssl_cred,
            quota_project_id=None,
        )
        assert transport.grpc_channel == mock_grpc_channel


def test_tenant_path():
    project = "squid"
    tenant = "clam"

    expected = "projects/{project}/tenants/{tenant}".format(
        project=project, tenant=tenant,
    )
    actual = TenantServiceClient.tenant_path(project, tenant)
    assert expected == actual


def test_parse_tenant_path():
    expected = {
        "project": "whelk",
        "tenant": "octopus",
    }
    path = TenantServiceClient.tenant_path(**expected)

    # Check that the path construction is reversible.
    actual = TenantServiceClient.parse_tenant_path(path)
    assert expected == actual
