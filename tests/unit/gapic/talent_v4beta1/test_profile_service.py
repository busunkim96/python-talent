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
from google.cloud.talent_v4beta1.services.profile_service import (
    ProfileServiceAsyncClient,
)
from google.cloud.talent_v4beta1.services.profile_service import ProfileServiceClient
from google.cloud.talent_v4beta1.services.profile_service import pagers
from google.cloud.talent_v4beta1.services.profile_service import transports
from google.cloud.talent_v4beta1.types import common
from google.cloud.talent_v4beta1.types import filters
from google.cloud.talent_v4beta1.types import histogram
from google.cloud.talent_v4beta1.types import profile
from google.cloud.talent_v4beta1.types import profile as gct_profile
from google.cloud.talent_v4beta1.types import profile_service
from google.oauth2 import service_account
from google.protobuf import duration_pb2 as duration  # type: ignore
from google.protobuf import field_mask_pb2 as field_mask  # type: ignore
from google.protobuf import timestamp_pb2 as timestamp  # type: ignore
from google.protobuf import wrappers_pb2 as wrappers  # type: ignore
from google.type import date_pb2 as date  # type: ignore
from google.type import latlng_pb2 as latlng  # type: ignore
from google.type import postal_address_pb2 as gt_postal_address  # type: ignore


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

    assert ProfileServiceClient._get_default_mtls_endpoint(None) is None
    assert (
        ProfileServiceClient._get_default_mtls_endpoint(api_endpoint)
        == api_mtls_endpoint
    )
    assert (
        ProfileServiceClient._get_default_mtls_endpoint(api_mtls_endpoint)
        == api_mtls_endpoint
    )
    assert (
        ProfileServiceClient._get_default_mtls_endpoint(sandbox_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        ProfileServiceClient._get_default_mtls_endpoint(sandbox_mtls_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        ProfileServiceClient._get_default_mtls_endpoint(non_googleapi) == non_googleapi
    )


@pytest.mark.parametrize(
    "client_class", [ProfileServiceClient, ProfileServiceAsyncClient]
)
def test_profile_service_client_from_service_account_file(client_class):
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


def test_profile_service_client_get_transport_class():
    transport = ProfileServiceClient.get_transport_class()
    assert transport == transports.ProfileServiceGrpcTransport

    transport = ProfileServiceClient.get_transport_class("grpc")
    assert transport == transports.ProfileServiceGrpcTransport


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (ProfileServiceClient, transports.ProfileServiceGrpcTransport, "grpc"),
        (
            ProfileServiceAsyncClient,
            transports.ProfileServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
@mock.patch.object(
    ProfileServiceClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(ProfileServiceClient),
)
@mock.patch.object(
    ProfileServiceAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(ProfileServiceAsyncClient),
)
def test_profile_service_client_client_options(
    client_class, transport_class, transport_name
):
    # Check that if channel is provided we won't create a new one.
    with mock.patch.object(ProfileServiceClient, "get_transport_class") as gtc:
        transport = transport_class(credentials=credentials.AnonymousCredentials())
        client = client_class(transport=transport)
        gtc.assert_not_called()

    # Check that if channel is provided via str we will create a new one.
    with mock.patch.object(ProfileServiceClient, "get_transport_class") as gtc:
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
        (ProfileServiceClient, transports.ProfileServiceGrpcTransport, "grpc"),
        (
            ProfileServiceAsyncClient,
            transports.ProfileServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_profile_service_client_client_options_scopes(
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
        (ProfileServiceClient, transports.ProfileServiceGrpcTransport, "grpc"),
        (
            ProfileServiceAsyncClient,
            transports.ProfileServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_profile_service_client_client_options_credentials_file(
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


def test_profile_service_client_client_options_from_dict():
    with mock.patch(
        "google.cloud.talent_v4beta1.services.profile_service.transports.ProfileServiceGrpcTransport.__init__"
    ) as grpc_transport:
        grpc_transport.return_value = None
        client = ProfileServiceClient(
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


def test_list_profiles(
    transport: str = "grpc", request_type=profile_service.ListProfilesRequest
):
    client = ProfileServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_profiles), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = profile_service.ListProfilesResponse(
            next_page_token="next_page_token_value",
        )

        response = client.list_profiles(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == profile_service.ListProfilesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListProfilesPager)

    assert response.next_page_token == "next_page_token_value"


def test_list_profiles_from_dict():
    test_list_profiles(request_type=dict)


@pytest.mark.asyncio
async def test_list_profiles_async(transport: str = "grpc_asyncio"):
    client = ProfileServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = profile_service.ListProfilesRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_profiles), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            profile_service.ListProfilesResponse(
                next_page_token="next_page_token_value",
            )
        )

        response = await client.list_profiles(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListProfilesAsyncPager)

    assert response.next_page_token == "next_page_token_value"


def test_list_profiles_field_headers():
    client = ProfileServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = profile_service.ListProfilesRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_profiles), "__call__") as call:
        call.return_value = profile_service.ListProfilesResponse()

        client.list_profiles(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_profiles_field_headers_async():
    client = ProfileServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = profile_service.ListProfilesRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_profiles), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            profile_service.ListProfilesResponse()
        )

        await client.list_profiles(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_profiles_flattened():
    client = ProfileServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_profiles), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = profile_service.ListProfilesResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_profiles(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"


def test_list_profiles_flattened_error():
    client = ProfileServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_profiles(
            profile_service.ListProfilesRequest(), parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_profiles_flattened_async():
    client = ProfileServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_profiles), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = profile_service.ListProfilesResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            profile_service.ListProfilesResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_profiles(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_list_profiles_flattened_error_async():
    client = ProfileServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_profiles(
            profile_service.ListProfilesRequest(), parent="parent_value",
        )


def test_list_profiles_pager():
    client = ProfileServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_profiles), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            profile_service.ListProfilesResponse(
                profiles=[profile.Profile(), profile.Profile(), profile.Profile(),],
                next_page_token="abc",
            ),
            profile_service.ListProfilesResponse(profiles=[], next_page_token="def",),
            profile_service.ListProfilesResponse(
                profiles=[profile.Profile(),], next_page_token="ghi",
            ),
            profile_service.ListProfilesResponse(
                profiles=[profile.Profile(), profile.Profile(),],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_profiles(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, profile.Profile) for i in results)


def test_list_profiles_pages():
    client = ProfileServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_profiles), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            profile_service.ListProfilesResponse(
                profiles=[profile.Profile(), profile.Profile(), profile.Profile(),],
                next_page_token="abc",
            ),
            profile_service.ListProfilesResponse(profiles=[], next_page_token="def",),
            profile_service.ListProfilesResponse(
                profiles=[profile.Profile(),], next_page_token="ghi",
            ),
            profile_service.ListProfilesResponse(
                profiles=[profile.Profile(), profile.Profile(),],
            ),
            RuntimeError,
        )
        pages = list(client.list_profiles(request={}).pages)
        for page, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_profiles_async_pager():
    client = ProfileServiceAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_profiles),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            profile_service.ListProfilesResponse(
                profiles=[profile.Profile(), profile.Profile(), profile.Profile(),],
                next_page_token="abc",
            ),
            profile_service.ListProfilesResponse(profiles=[], next_page_token="def",),
            profile_service.ListProfilesResponse(
                profiles=[profile.Profile(),], next_page_token="ghi",
            ),
            profile_service.ListProfilesResponse(
                profiles=[profile.Profile(), profile.Profile(),],
            ),
            RuntimeError,
        )
        async_pager = await client.list_profiles(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, profile.Profile) for i in responses)


@pytest.mark.asyncio
async def test_list_profiles_async_pages():
    client = ProfileServiceAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_profiles),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            profile_service.ListProfilesResponse(
                profiles=[profile.Profile(), profile.Profile(), profile.Profile(),],
                next_page_token="abc",
            ),
            profile_service.ListProfilesResponse(profiles=[], next_page_token="def",),
            profile_service.ListProfilesResponse(
                profiles=[profile.Profile(),], next_page_token="ghi",
            ),
            profile_service.ListProfilesResponse(
                profiles=[profile.Profile(), profile.Profile(),],
            ),
            RuntimeError,
        )
        pages = []
        async for page in (await client.list_profiles(request={})).pages:
            pages.append(page)
        for page, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page.raw_page.next_page_token == token


def test_create_profile(
    transport: str = "grpc", request_type=profile_service.CreateProfileRequest
):
    client = ProfileServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.create_profile), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gct_profile.Profile(
            name="name_value",
            external_id="external_id_value",
            source="source_value",
            uri="uri_value",
            group_id="group_id_value",
            applications=["applications_value"],
            assignments=["assignments_value"],
            processed=True,
            keyword_snippet="keyword_snippet_value",
        )

        response = client.create_profile(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == profile_service.CreateProfileRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gct_profile.Profile)

    assert response.name == "name_value"

    assert response.external_id == "external_id_value"

    assert response.source == "source_value"

    assert response.uri == "uri_value"

    assert response.group_id == "group_id_value"

    assert response.applications == ["applications_value"]

    assert response.assignments == ["assignments_value"]

    assert response.processed is True

    assert response.keyword_snippet == "keyword_snippet_value"


def test_create_profile_from_dict():
    test_create_profile(request_type=dict)


@pytest.mark.asyncio
async def test_create_profile_async(transport: str = "grpc_asyncio"):
    client = ProfileServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = profile_service.CreateProfileRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_profile), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gct_profile.Profile(
                name="name_value",
                external_id="external_id_value",
                source="source_value",
                uri="uri_value",
                group_id="group_id_value",
                applications=["applications_value"],
                assignments=["assignments_value"],
                processed=True,
                keyword_snippet="keyword_snippet_value",
            )
        )

        response = await client.create_profile(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gct_profile.Profile)

    assert response.name == "name_value"

    assert response.external_id == "external_id_value"

    assert response.source == "source_value"

    assert response.uri == "uri_value"

    assert response.group_id == "group_id_value"

    assert response.applications == ["applications_value"]

    assert response.assignments == ["assignments_value"]

    assert response.processed is True

    assert response.keyword_snippet == "keyword_snippet_value"


def test_create_profile_field_headers():
    client = ProfileServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = profile_service.CreateProfileRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.create_profile), "__call__") as call:
        call.return_value = gct_profile.Profile()

        client.create_profile(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_profile_field_headers_async():
    client = ProfileServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = profile_service.CreateProfileRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_profile), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gct_profile.Profile())

        await client.create_profile(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_create_profile_flattened():
    client = ProfileServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.create_profile), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gct_profile.Profile()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_profile(
            parent="parent_value", profile=gct_profile.Profile(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].profile == gct_profile.Profile(name="name_value")


def test_create_profile_flattened_error():
    client = ProfileServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_profile(
            profile_service.CreateProfileRequest(),
            parent="parent_value",
            profile=gct_profile.Profile(name="name_value"),
        )


@pytest.mark.asyncio
async def test_create_profile_flattened_async():
    client = ProfileServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_profile), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gct_profile.Profile()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gct_profile.Profile())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_profile(
            parent="parent_value", profile=gct_profile.Profile(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].profile == gct_profile.Profile(name="name_value")


@pytest.mark.asyncio
async def test_create_profile_flattened_error_async():
    client = ProfileServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_profile(
            profile_service.CreateProfileRequest(),
            parent="parent_value",
            profile=gct_profile.Profile(name="name_value"),
        )


def test_get_profile(
    transport: str = "grpc", request_type=profile_service.GetProfileRequest
):
    client = ProfileServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_profile), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = profile.Profile(
            name="name_value",
            external_id="external_id_value",
            source="source_value",
            uri="uri_value",
            group_id="group_id_value",
            applications=["applications_value"],
            assignments=["assignments_value"],
            processed=True,
            keyword_snippet="keyword_snippet_value",
        )

        response = client.get_profile(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == profile_service.GetProfileRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, profile.Profile)

    assert response.name == "name_value"

    assert response.external_id == "external_id_value"

    assert response.source == "source_value"

    assert response.uri == "uri_value"

    assert response.group_id == "group_id_value"

    assert response.applications == ["applications_value"]

    assert response.assignments == ["assignments_value"]

    assert response.processed is True

    assert response.keyword_snippet == "keyword_snippet_value"


def test_get_profile_from_dict():
    test_get_profile(request_type=dict)


@pytest.mark.asyncio
async def test_get_profile_async(transport: str = "grpc_asyncio"):
    client = ProfileServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = profile_service.GetProfileRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_profile), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            profile.Profile(
                name="name_value",
                external_id="external_id_value",
                source="source_value",
                uri="uri_value",
                group_id="group_id_value",
                applications=["applications_value"],
                assignments=["assignments_value"],
                processed=True,
                keyword_snippet="keyword_snippet_value",
            )
        )

        response = await client.get_profile(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, profile.Profile)

    assert response.name == "name_value"

    assert response.external_id == "external_id_value"

    assert response.source == "source_value"

    assert response.uri == "uri_value"

    assert response.group_id == "group_id_value"

    assert response.applications == ["applications_value"]

    assert response.assignments == ["assignments_value"]

    assert response.processed is True

    assert response.keyword_snippet == "keyword_snippet_value"


def test_get_profile_field_headers():
    client = ProfileServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = profile_service.GetProfileRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_profile), "__call__") as call:
        call.return_value = profile.Profile()

        client.get_profile(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_profile_field_headers_async():
    client = ProfileServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = profile_service.GetProfileRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_profile), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(profile.Profile())

        await client.get_profile(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_profile_flattened():
    client = ProfileServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_profile), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = profile.Profile()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_profile(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_get_profile_flattened_error():
    client = ProfileServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_profile(
            profile_service.GetProfileRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_profile_flattened_async():
    client = ProfileServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_profile), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = profile.Profile()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(profile.Profile())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_profile(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_profile_flattened_error_async():
    client = ProfileServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_profile(
            profile_service.GetProfileRequest(), name="name_value",
        )


def test_update_profile(
    transport: str = "grpc", request_type=profile_service.UpdateProfileRequest
):
    client = ProfileServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.update_profile), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gct_profile.Profile(
            name="name_value",
            external_id="external_id_value",
            source="source_value",
            uri="uri_value",
            group_id="group_id_value",
            applications=["applications_value"],
            assignments=["assignments_value"],
            processed=True,
            keyword_snippet="keyword_snippet_value",
        )

        response = client.update_profile(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == profile_service.UpdateProfileRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gct_profile.Profile)

    assert response.name == "name_value"

    assert response.external_id == "external_id_value"

    assert response.source == "source_value"

    assert response.uri == "uri_value"

    assert response.group_id == "group_id_value"

    assert response.applications == ["applications_value"]

    assert response.assignments == ["assignments_value"]

    assert response.processed is True

    assert response.keyword_snippet == "keyword_snippet_value"


def test_update_profile_from_dict():
    test_update_profile(request_type=dict)


@pytest.mark.asyncio
async def test_update_profile_async(transport: str = "grpc_asyncio"):
    client = ProfileServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = profile_service.UpdateProfileRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_profile), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gct_profile.Profile(
                name="name_value",
                external_id="external_id_value",
                source="source_value",
                uri="uri_value",
                group_id="group_id_value",
                applications=["applications_value"],
                assignments=["assignments_value"],
                processed=True,
                keyword_snippet="keyword_snippet_value",
            )
        )

        response = await client.update_profile(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gct_profile.Profile)

    assert response.name == "name_value"

    assert response.external_id == "external_id_value"

    assert response.source == "source_value"

    assert response.uri == "uri_value"

    assert response.group_id == "group_id_value"

    assert response.applications == ["applications_value"]

    assert response.assignments == ["assignments_value"]

    assert response.processed is True

    assert response.keyword_snippet == "keyword_snippet_value"


def test_update_profile_field_headers():
    client = ProfileServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = profile_service.UpdateProfileRequest()
    request.profile.name = "profile.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.update_profile), "__call__") as call:
        call.return_value = gct_profile.Profile()

        client.update_profile(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "profile.name=profile.name/value",) in kw[
        "metadata"
    ]


@pytest.mark.asyncio
async def test_update_profile_field_headers_async():
    client = ProfileServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = profile_service.UpdateProfileRequest()
    request.profile.name = "profile.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_profile), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gct_profile.Profile())

        await client.update_profile(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "profile.name=profile.name/value",) in kw[
        "metadata"
    ]


def test_update_profile_flattened():
    client = ProfileServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.update_profile), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gct_profile.Profile()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_profile(profile=gct_profile.Profile(name="name_value"),)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].profile == gct_profile.Profile(name="name_value")


def test_update_profile_flattened_error():
    client = ProfileServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_profile(
            profile_service.UpdateProfileRequest(),
            profile=gct_profile.Profile(name="name_value"),
        )


@pytest.mark.asyncio
async def test_update_profile_flattened_async():
    client = ProfileServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_profile), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gct_profile.Profile()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gct_profile.Profile())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_profile(
            profile=gct_profile.Profile(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].profile == gct_profile.Profile(name="name_value")


@pytest.mark.asyncio
async def test_update_profile_flattened_error_async():
    client = ProfileServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_profile(
            profile_service.UpdateProfileRequest(),
            profile=gct_profile.Profile(name="name_value"),
        )


def test_delete_profile(
    transport: str = "grpc", request_type=profile_service.DeleteProfileRequest
):
    client = ProfileServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.delete_profile), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        response = client.delete_profile(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == profile_service.DeleteProfileRequest()

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_profile_from_dict():
    test_delete_profile(request_type=dict)


@pytest.mark.asyncio
async def test_delete_profile_async(transport: str = "grpc_asyncio"):
    client = ProfileServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = profile_service.DeleteProfileRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_profile), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        response = await client.delete_profile(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_profile_field_headers():
    client = ProfileServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = profile_service.DeleteProfileRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.delete_profile), "__call__") as call:
        call.return_value = None

        client.delete_profile(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_profile_field_headers_async():
    client = ProfileServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = profile_service.DeleteProfileRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_profile), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        await client.delete_profile(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_delete_profile_flattened():
    client = ProfileServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.delete_profile), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_profile(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_delete_profile_flattened_error():
    client = ProfileServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_profile(
            profile_service.DeleteProfileRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_profile_flattened_async():
    client = ProfileServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_profile), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_profile(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_delete_profile_flattened_error_async():
    client = ProfileServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_profile(
            profile_service.DeleteProfileRequest(), name="name_value",
        )


def test_search_profiles(
    transport: str = "grpc", request_type=profile_service.SearchProfilesRequest
):
    client = ProfileServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.search_profiles), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = profile_service.SearchProfilesResponse(
            estimated_total_size=2141,
            next_page_token="next_page_token_value",
            result_set_id="result_set_id_value",
        )

        response = client.search_profiles(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == profile_service.SearchProfilesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.SearchProfilesPager)

    assert response.estimated_total_size == 2141

    assert response.next_page_token == "next_page_token_value"

    assert response.result_set_id == "result_set_id_value"


def test_search_profiles_from_dict():
    test_search_profiles(request_type=dict)


@pytest.mark.asyncio
async def test_search_profiles_async(transport: str = "grpc_asyncio"):
    client = ProfileServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = profile_service.SearchProfilesRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.search_profiles), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            profile_service.SearchProfilesResponse(
                estimated_total_size=2141,
                next_page_token="next_page_token_value",
                result_set_id="result_set_id_value",
            )
        )

        response = await client.search_profiles(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.SearchProfilesAsyncPager)

    assert response.estimated_total_size == 2141

    assert response.next_page_token == "next_page_token_value"

    assert response.result_set_id == "result_set_id_value"


def test_search_profiles_field_headers():
    client = ProfileServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = profile_service.SearchProfilesRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.search_profiles), "__call__") as call:
        call.return_value = profile_service.SearchProfilesResponse()

        client.search_profiles(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_search_profiles_field_headers_async():
    client = ProfileServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = profile_service.SearchProfilesRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.search_profiles), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            profile_service.SearchProfilesResponse()
        )

        await client.search_profiles(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_search_profiles_pager():
    client = ProfileServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.search_profiles), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            profile_service.SearchProfilesResponse(
                histogram_query_results=[
                    histogram.HistogramQueryResult(),
                    histogram.HistogramQueryResult(),
                    histogram.HistogramQueryResult(),
                ],
                next_page_token="abc",
            ),
            profile_service.SearchProfilesResponse(
                histogram_query_results=[], next_page_token="def",
            ),
            profile_service.SearchProfilesResponse(
                histogram_query_results=[histogram.HistogramQueryResult(),],
                next_page_token="ghi",
            ),
            profile_service.SearchProfilesResponse(
                histogram_query_results=[
                    histogram.HistogramQueryResult(),
                    histogram.HistogramQueryResult(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.search_profiles(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, histogram.HistogramQueryResult) for i in results)


def test_search_profiles_pages():
    client = ProfileServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.search_profiles), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            profile_service.SearchProfilesResponse(
                histogram_query_results=[
                    histogram.HistogramQueryResult(),
                    histogram.HistogramQueryResult(),
                    histogram.HistogramQueryResult(),
                ],
                next_page_token="abc",
            ),
            profile_service.SearchProfilesResponse(
                histogram_query_results=[], next_page_token="def",
            ),
            profile_service.SearchProfilesResponse(
                histogram_query_results=[histogram.HistogramQueryResult(),],
                next_page_token="ghi",
            ),
            profile_service.SearchProfilesResponse(
                histogram_query_results=[
                    histogram.HistogramQueryResult(),
                    histogram.HistogramQueryResult(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.search_profiles(request={}).pages)
        for page, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_search_profiles_async_pager():
    client = ProfileServiceAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.search_profiles),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            profile_service.SearchProfilesResponse(
                histogram_query_results=[
                    histogram.HistogramQueryResult(),
                    histogram.HistogramQueryResult(),
                    histogram.HistogramQueryResult(),
                ],
                next_page_token="abc",
            ),
            profile_service.SearchProfilesResponse(
                histogram_query_results=[], next_page_token="def",
            ),
            profile_service.SearchProfilesResponse(
                histogram_query_results=[histogram.HistogramQueryResult(),],
                next_page_token="ghi",
            ),
            profile_service.SearchProfilesResponse(
                histogram_query_results=[
                    histogram.HistogramQueryResult(),
                    histogram.HistogramQueryResult(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.search_profiles(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, histogram.HistogramQueryResult) for i in responses)


@pytest.mark.asyncio
async def test_search_profiles_async_pages():
    client = ProfileServiceAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.search_profiles),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            profile_service.SearchProfilesResponse(
                histogram_query_results=[
                    histogram.HistogramQueryResult(),
                    histogram.HistogramQueryResult(),
                    histogram.HistogramQueryResult(),
                ],
                next_page_token="abc",
            ),
            profile_service.SearchProfilesResponse(
                histogram_query_results=[], next_page_token="def",
            ),
            profile_service.SearchProfilesResponse(
                histogram_query_results=[histogram.HistogramQueryResult(),],
                next_page_token="ghi",
            ),
            profile_service.SearchProfilesResponse(
                histogram_query_results=[
                    histogram.HistogramQueryResult(),
                    histogram.HistogramQueryResult(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        async for page in (await client.search_profiles(request={})).pages:
            pages.append(page)
        for page, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page.raw_page.next_page_token == token


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.ProfileServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = ProfileServiceClient(
            credentials=credentials.AnonymousCredentials(), transport=transport,
        )

    # It is an error to provide a credentials file and a transport instance.
    transport = transports.ProfileServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = ProfileServiceClient(
            client_options={"credentials_file": "credentials.json"},
            transport=transport,
        )

    # It is an error to provide scopes and a transport instance.
    transport = transports.ProfileServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = ProfileServiceClient(
            client_options={"scopes": ["1", "2"]}, transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.ProfileServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    client = ProfileServiceClient(transport=transport)
    assert client._transport is transport


def test_transport_get_channel():
    # A client may be instantiated with a custom transport instance.
    transport = transports.ProfileServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel

    transport = transports.ProfileServiceGrpcAsyncIOTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel


def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = ProfileServiceClient(credentials=credentials.AnonymousCredentials(),)
    assert isinstance(client._transport, transports.ProfileServiceGrpcTransport,)


def test_profile_service_base_transport_error():
    # Passing both a credentials object and credentials_file should raise an error
    with pytest.raises(exceptions.DuplicateCredentialArgs):
        transport = transports.ProfileServiceTransport(
            credentials=credentials.AnonymousCredentials(),
            credentials_file="credentials.json",
        )


def test_profile_service_base_transport():
    # Instantiate the base transport.
    with mock.patch(
        "google.cloud.talent_v4beta1.services.profile_service.transports.ProfileServiceTransport.__init__"
    ) as Transport:
        Transport.return_value = None
        transport = transports.ProfileServiceTransport(
            credentials=credentials.AnonymousCredentials(),
        )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        "list_profiles",
        "create_profile",
        "get_profile",
        "update_profile",
        "delete_profile",
        "search_profiles",
    )
    for method in methods:
        with pytest.raises(NotImplementedError):
            getattr(transport, method)(request=object())


def test_profile_service_base_transport_with_credentials_file():
    # Instantiate the base transport with a credentials file
    with mock.patch.object(
        auth, "load_credentials_from_file"
    ) as load_creds, mock.patch(
        "google.cloud.talent_v4beta1.services.profile_service.transports.ProfileServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        load_creds.return_value = (credentials.AnonymousCredentials(), None)
        transport = transports.ProfileServiceTransport(
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


def test_profile_service_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        ProfileServiceClient()
        adc.assert_called_once_with(
            scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/jobs",
            ),
            quota_project_id=None,
        )


def test_profile_service_transport_auth_adc():
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        transports.ProfileServiceGrpcTransport(
            host="squid.clam.whelk", quota_project_id="octopus"
        )
        adc.assert_called_once_with(
            scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/jobs",
            ),
            quota_project_id="octopus",
        )


def test_profile_service_host_no_port():
    client = ProfileServiceClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(api_endpoint="jobs.googleapis.com"),
    )
    assert client._transport._host == "jobs.googleapis.com:443"


def test_profile_service_host_with_port():
    client = ProfileServiceClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="jobs.googleapis.com:8000"
        ),
    )
    assert client._transport._host == "jobs.googleapis.com:8000"


def test_profile_service_grpc_transport_channel():
    channel = grpc.insecure_channel("http://localhost/")

    # Check that if channel is provided, mtls endpoint and client_cert_source
    # won't be used.
    callback = mock.MagicMock()
    transport = transports.ProfileServiceGrpcTransport(
        host="squid.clam.whelk",
        channel=channel,
        api_mtls_endpoint="mtls.squid.clam.whelk",
        client_cert_source=callback,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert not callback.called


def test_profile_service_grpc_asyncio_transport_channel():
    channel = aio.insecure_channel("http://localhost/")

    # Check that if channel is provided, mtls endpoint and client_cert_source
    # won't be used.
    callback = mock.MagicMock()
    transport = transports.ProfileServiceGrpcAsyncIOTransport(
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
def test_profile_service_grpc_transport_channel_mtls_with_client_cert_source(
    grpc_create_channel, grpc_ssl_channel_cred
):
    # Check that if channel is None, but api_mtls_endpoint and client_cert_source
    # are provided, then a mTLS channel will be created.
    mock_cred = mock.Mock()

    mock_ssl_cred = mock.Mock()
    grpc_ssl_channel_cred.return_value = mock_ssl_cred

    mock_grpc_channel = mock.Mock()
    grpc_create_channel.return_value = mock_grpc_channel

    transport = transports.ProfileServiceGrpcTransport(
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
def test_profile_service_grpc_asyncio_transport_channel_mtls_with_client_cert_source(
    grpc_create_channel, grpc_ssl_channel_cred
):
    # Check that if channel is None, but api_mtls_endpoint and client_cert_source
    # are provided, then a mTLS channel will be created.
    mock_cred = mock.Mock()

    mock_ssl_cred = mock.Mock()
    grpc_ssl_channel_cred.return_value = mock_ssl_cred

    mock_grpc_channel = mock.Mock()
    grpc_create_channel.return_value = mock_grpc_channel

    transport = transports.ProfileServiceGrpcAsyncIOTransport(
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
def test_profile_service_grpc_transport_channel_mtls_with_adc(
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
        transport = transports.ProfileServiceGrpcTransport(
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
def test_profile_service_grpc_asyncio_transport_channel_mtls_with_adc(
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
        transport = transports.ProfileServiceGrpcAsyncIOTransport(
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


def test_profile_path():
    project = "squid"
    tenant = "clam"
    profile = "whelk"

    expected = "projects/{project}/tenants/{tenant}/profiles/{profile}".format(
        project=project, tenant=tenant, profile=profile,
    )
    actual = ProfileServiceClient.profile_path(project, tenant, profile)
    assert expected == actual


def test_parse_profile_path():
    expected = {
        "project": "octopus",
        "tenant": "oyster",
        "profile": "nudibranch",
    }
    path = ProfileServiceClient.profile_path(**expected)

    # Check that the path construction is reversible.
    actual = ProfileServiceClient.parse_profile_path(path)
    assert expected == actual
