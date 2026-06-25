# servers/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Server, Channel, Category, ServerMember
from chat.models import Message
from accounts.models import User

@login_required
def home(request):
    servers = Server.objects.filter(members=request.user)
    friends = request.user.friends.filter(friendship_to__accepted=True)
    
    context = {
        'servers': servers,
        'friends': friends,
        'friend_requests': request.user.received_requests.filter(accepted=False, declined=False),
    }
    return render(request, 'servers/home.html', context)

@login_required
def server_view(request, server_id, channel_id=None):
    server = get_object_or_404(Server, id=server_id)
    
    # Проверяем, является ли пользователь участником сервера
    if not ServerMember.objects.filter(server=server, user=request.user).exists():
        messages.error(request, 'Вы не являетесь участником этого сервера')
        return redirect('home')
    
    categories = server.categories.all()
    channels = server.channels.all()
    
    if channel_id:
        current_channel = get_object_or_404(Channel, id=channel_id, server=server)
    else:
        current_channel = channels.filter(channel_type='text').first()
    
    messages_list = []
    if current_channel:
        messages_list = Message.objects.filter(channel=current_channel).order_by('timestamp')[:50]
    
    members = ServerMember.objects.filter(server=server).select_related('user')
    
    context = {
        'server': server,
        'categories': categories,
        'channels': channels,
        'current_channel': current_channel,
        'messages': messages_list,
        'members': members,
        'is_owner': server.owner == request.user,
    }
    return render(request, 'servers/server.html', context)

@login_required
def create_server(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        if name:
            server = Server.objects.create(
                name=name,
                owner=request.user,
                description=description
            )
            
            # Добавляем создателя как участника
            ServerMember.objects.create(
                user=request.user,
                server=server,
                role='owner'
            )
            
            # Создаем базовую категорию и канал
            category = Category.objects.create(
                server=server,
                name='Основные',
                position=0
            )
            
            Channel.objects.create(
                server=server,
                category=category,
                name='общий',
                channel_type='text',
                position=0
            )
            
            return redirect('server_view', server_id=server.id)
    
    return render(request, 'servers/create_server.html')

@login_required
def create_channel(request, server_id):
    server = get_object_or_404(Server, id=server_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        channel_type = request.POST.get('channel_type', 'text')
        category_id = request.POST.get('category')
        
        if name:
            channel = Channel.objects.create(
                server=server,
                name=name,
                channel_type=channel_type,
                category_id=category_id if category_id else None
            )
            
            return JsonResponse({
                'success': True,
                'channel_id': channel.id,
                'channel_name': channel.name
            })
    
    return JsonResponse({'success': False})

@login_required
def join_server(request, invite_code):
    try:
        server = Server.objects.get(invite_code=invite_code)
        
        if ServerMember.objects.filter(server=server, user=request.user).exists():
            messages.info(request, 'Вы уже участник этого сервера')
        else:
            ServerMember.objects.create(user=request.user, server=server)
            messages.success(request, f'Вы присоединились к серверу {server.name}')
        
        return redirect('server_view', server_id=server.id)
    except Server.DoesNotExist:
        messages.error(request, 'Неверный код приглашения')
        return redirect('home')

@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        from accounts.models import FriendRequest
        FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user)
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    friend_request.accepted = True
    friend_request.save()
    
    # Создаем дружбу в обе стороны
    Friendship.objects.get_or_create(from_user=friend_request.from_user, to_user=friend_request.to_user)
    Friendship.objects.get_or_create(from_user=friend_request.to_user, to_user=friend_request.from_user)
    
    return JsonResponse({'success': True})

@login_required
def direct_messages(request, user_id=None):
    friends = request.user.friends.all()
    current_friend = None
    messages_list = []
    
    if user_id:
        current_friend = get_object_or_404(User, id=user_id)
        messages_list = DirectMessage.objects.filter(
            sender__in=[request.user, current_friend],
            recipient__in=[request.user, current_friend]
        ).order_by('timestamp')[:50]
    
    context = {
        'friends': friends,
        'current_friend': current_friend,
        'messages': messages_list,
    }
    return render(request, 'chat/direct_messages.html', context)