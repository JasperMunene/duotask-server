from .helpers import first_name

full_logo = "https://res.cloudinary.com/dfvauxrrg/image/upload/v1763130303/full_scpz7t.png"
favicon_logo = "https://res.cloudinary.com/dfvauxrrg/image/upload/v1763130303/logo_pjlj60.png"
def verification_email_template(name, token):
    name = first_name(name)
    return f"""
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; color: #1a1a1a; padding: 20px; margin: 0; min-height: 100vh;">
        <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); overflow: hidden;">
            
            <!-- Header -->
            <div style="background: #ffffff; padding: 32px 40px 24px; text-align: center; border-bottom: 1px solid #f0f0f0;">
                <img src="{full_logo}" alt="duotasks" style="height: 150px; width: auto; margin-bottom: 8px;">
            </div>
            
            <!-- Main Content -->
            <div style="padding: 48px 40px;">
                <!-- Welcome Section -->
                <div style="text-align: center; margin-bottom: 40px;">
                    <h1 style="margin: 0 0 16px; font-size: 28px; font-weight: 600; color: #1a1a1a; line-height: 1.3;">
                        Welcome to Duotasks, {name}
                    </h1>
                    <p style="margin: 0; font-size: 18px; color: #6b7280; line-height: 1.5;">
                        Thank you for joining our community of skilled professionals and opportunity seekers
                    </p>
                </div>
                
                <!-- Verification Code Section -->
                <div style="background: #f8fffe; border: 2px solid #dcfce7; border-radius: 16px; padding: 32px; text-align: center; margin-bottom: 32px;">
                    <p style="margin: 0 0 24px; font-size: 16px; color: #374151; font-weight: 500;">
                        To complete your registration, please use this verification code:
                    </p>
                    <div style="background: #00915a; color: white; padding: 20px 32px; border-radius: 12px; display: inline-block; box-shadow: 0 4px 16px rgba(76, 175, 80, 0.25);">
                        <span style="font-size: 32px; font-weight: 700; letter-spacing: 6px; font-family: 'Courier New', monospace;">
                            {token}
                        </span>
                    </div>
                    <div style="margin-top: 24px; padding: 16px; background: #fef3c7; border-radius: 8px; border-left: 4px solid #f59e0b;">
                        <p style="margin: 0; font-size: 14px; color: #92400e; font-weight: 500;">
                            This code expires in 30 minutes
                        </p>
                    </div>
                </div>
                
                <!-- Platform Benefits -->
                <div style="background: #f9fafb; border-radius: 12px; padding: 24px; margin-bottom: 32px;">
                    <h3 style="margin: 0 0 16px; font-size: 18px; color: #1f2937; font-weight: 600;">
                        What you can do with duotasks:
                    </h3>
                    <div style="color: #4b5563; line-height: 1.6;">
                        <p style="margin: 0 0 8px;">• Connect with trusted local professionals</p>
                        <p style="margin: 0 0 8px;">• Post tasks and find skilled help nearby</p>
                        <p style="margin: 0 0 8px;">• Build your reputation in the community</p>
                        <p style="margin: 0;">• Experience fair pricing and secure payments</p>
                    </div>
                </div>
                
                <!-- Security Notice -->
                <div style="text-align: center; margin-bottom: 32px;">
                    <p style="margin: 0; font-size: 14px; color: #6b7280; line-height: 1.5;">
                        If you didn't create a duotasks account, you can safely ignore this email.<br>
                        For your security, never share this verification code with anyone.
                    </p>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background: #f9fafb; padding: 32px 40px; border-top: 1px solid #f0f0f0;">
                <div style="text-align: center;">
                    <img src="{full_logo}" alt="duotasks" style="height: 50px; width: auto; margin-bottom: 16px; opacity: 0.7;">
                    <p style="margin: 0 0 8px; font-size: 16px; color: #1f2937; font-weight: 600;">
                        duotasks
                    </p>
                    <p style="margin: 0 0 16px; font-size: 14px; color: #6b7280;">
                        Community. ✨
                    </p>
                    <div style="margin-bottom: 16px;">
                        <a href="https://duotasks.net" style="color: #00915a; text-decoration: none; font-size: 14px; margin: 0 12px;">
                            Visit Website
                        </a>
                        <a href="mailto:support@duotasks.net" style="color: #00915a; text-decoration: none; font-size: 14px; margin: 0 12px;">
                            Contact Support
                        </a>
                    </div>
                    <div style="border-top: 1px solid #e5e7eb; padding-top: 16px;">
                        <p style="margin: 0; font-size: 12px; color: #9ca3af;">
                            © 2025 duotasks. All rights reserved.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </body>
    """


def password_recovery_email_template(name, token):
    name = first_name(name)
    return f"""
    <body>
        <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); overflow: hidden;">
            
            <!-- Header -->
            <div style="background: #ffffff; padding: 32px 40px 24px; text-align: center; border-bottom: 1px solid #f0f0f0;">
                <img src="{full_logo}" alt="duotasks" style="height: 150px; width: auto; margin-bottom: 8px;">
            </div>
            
            <!-- Main Content -->
            <div style="padding: 48px 40px;">
                <!-- Security Alert Section -->
                <div style="text-align: center; margin-bottom: 40px;">
                    <h1 style="margin: 0 0 16px; font-size: 28px; font-weight: 600; color: #1a1a1a; line-height: 1.3;">
                        Password Reset Request
                    </h1>
                    <p style="margin: 0; font-size: 18px; color: #6b7280; line-height: 1.5;">
                        Hi {name}, we received a request to reset your duotasks password
                    </p>
                </div>
                
                <!-- Verification Code Section -->
                <div style="background: #fef2f2; border: 2px solid #fecaca; border-radius: 16px; padding: 32px; text-align: center; margin-bottom: 32px;">
                    <p style="margin: 0 0 24px; font-size: 16px; color: #374151; font-weight: 500;">
                        Use this verification code to reset your password:
                    </p>
                    <div style="background: #E53935; color: white; padding: 20px 32px; border-radius: 12px; display: inline-block; box-shadow: 0 4px 16px rgba(229, 57, 53, 0.25);">
                        <span style="font-size: 32px; font-weight: 700; letter-spacing: 6px; font-family: 'Courier New', monospace;">
                            {token}
                        </span>
                    </div>
                    <div style="margin-top: 24px; padding: 16px; background: #fef3c7; border-radius: 8px; border-left: 4px solid #f59e0b;">
                        <p style="margin: 0; font-size: 14px; color: #92400e; font-weight: 500;">
                            This code expires in 15 minutes for your security
                        </p>
                    </div>
                </div>
                
                <!-- Security Steps -->
                <div style="background: #f9fafb; border-radius: 12px; padding: 24px; margin-bottom: 32px;">
                    <h3 style="margin: 0 0 16px; font-size: 18px; color: #1f2937; font-weight: 600;">
                        Steps to secure your account:
                    </h3>
                    <div style="color: #4b5563; line-height: 1.6;">
                        <p style="margin: 0 0 8px;">• Enter the verification code above</p>
                        <p style="margin: 0 0 8px;">• Create a strong, unique password</p>
                        <p style="margin: 0 0 8px;">• Confirm your new password</p>
                        <p style="margin: 0;">• Sign in securely with new credentials</p>
                    </div>
                </div>
                
                <!-- Security Tips -->
                <div style="background: #ecfdf5; border: 1px solid #d1fae5; border-radius: 12px; padding: 24px; margin-bottom: 32px;">
                    <h4 style="margin: 0 0 12px; font-size: 16px; color: #065f46; font-weight: 600;">
                        Creating a secure password:
                    </h4>
                    <div style="color: #047857; line-height: 1.6; font-size: 14px;">
                        <p style="margin: 0 0 6px;">• Use at least 8 characters with mixed case and numbers</p>
                        <p style="margin: 0 0 6px;">• Avoid personal information or common phrases</p>
                        <p style="margin: 0;">• Consider using a trusted password manager</p>
                    </div>
                </div>
                
                <!-- Security Notice -->
                <div style="text-align: center; margin-bottom: 32px;">
                    <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 20px;">
                        <p style="margin: 0; font-size: 14px; color: #991b1b; line-height: 1.5; font-weight: 500;">
                            Didn't request a password reset?<br>
                            Your account remains secure. You can safely ignore this email.<br>
                            Never share this verification code with anyone.
                        </p>
                    </div>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background: #f9fafb; padding: 32px 40px; border-top: 1px solid #f0f0f0;">
                <div style="text-align: center;">
                    <img src="{favicon_logo}" alt="duotasks" style="height: 100px; width: auto; margin-bottom: 16px; opacity: 0.7;">
                    <p style="margin: 0 0 8px; font-size: 16px; color: #1f2937; font-weight: 600;">
                        duotasks Security Team
                    </p>
                    <p style="margin: 0 0 16px; font-size: 14px; color: #6b7280;">
                        Protecting your account and privacy
                    </p>
                    <div style="margin-bottom: 16px;">
                        <a href="https://duotasks.net" style="color: #E53935; text-decoration: none; font-size: 14px; margin: 0 12px;">
                            Visit Website
                        </a>
                        <a href="mailto:support@duotasks.net" style="color: #E53935; text-decoration: none; font-size: 14px; margin: 0 12px;">
                            Contact Support
                        </a>
                    </div>
                    <div style="border-top: 1px solid #e5e7eb; padding-top: 16px;">
                        <p style="margin: 0; font-size: 12px; color: #9ca3af;">
                            © 2025 duotasks. All rights reserved.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </body>
    """

def wallet_topup_email_template(name, transaction_id, amount, timestamp, payment_method="mpesa"):
    name = first_name(name)
    return f"""
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; color: #1a1a1a; padding: 20px; margin: 0; min-height: 100vh;">
        <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); overflow: hidden;">
            
            <!-- Header -->
            <div style="background: #ffffff; padding: 32px 40px 24px; text-align: center; border-bottom: 1px solid #f0f0f0;">
                <img src="{full_logo}" alt="duotasks" style="height: 150px; width: auto; margin-bottom: 8px;">
            </div>
            
            <!-- Main Content -->
            <div style="padding: 48px 40px;">
                <!-- Success Section -->
                <div style="text-align: center; margin-bottom: 40px;">
                    <h1 style="margin: 0 0 16px; font-size: 28px; font-weight: 600; color: #1a1a1a; line-height: 1.3;">
                        Top-up Successful!
                    </h1>
                    <p style="margin: 0; font-size: 18px; color: #6b7280; line-height: 1.5;">
                        Hi {name}, your wallet has been credited successfully
                    </p>
                </div>
                
                <!-- Transaction Details Section -->
                <div style="background: #f8fffe; border: 2px solid #dcfce7; border-radius: 16px; padding: 32px; margin-bottom: 32px;">
                    <h3 style="margin: 0 0 24px; font-size: 18px; color: #1f2937; font-weight: 600; text-align: center;">
                        Transaction Details
                    </h3>
                    
                    <!-- Amount Display -->
                    <div style="text-align: center; margin-bottom: 24px; padding-bottom: 24px; border-bottom: 1px solid #d1fae5;">
                        <p style="margin: 0 0 8px; font-size: 14px; color: #6b7280; text-transform: uppercase; letter-spacing: 1px;">
                            Amount Credited
                        </p>
                        <div style="background: #00915a; color: white; padding: 16px 24px; border-radius: 12px; display: inline-block; box-shadow: 0 4px 16px rgba(0, 145, 90, 0.25);">
                            <span style="font-size: 36px; font-weight: 700; font-family: 'Courier New', monospace;">
                                KES {amount:,.2f}
                            </span>
                        </div>
                    </div>
                    
                    <!-- Transaction Info Grid -->
                    <div style="color: #4b5563; line-height: 1.8;">
                        <div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #e5e7eb;">
                            <span style="font-weight: 500; color: #6b7280;">Transaction ID:</span>
                            <span style="font-weight: 600; color: #1f2937; font-family: 'Courier New', monospace;">{transaction_id}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #e5e7eb;">
                            <span style="font-weight: 500; color: #6b7280;">Payment Method:</span>
                            <span style="font-weight: 600; color: #1f2937;">{payment_method}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #e5e7eb;">
                            <span style="font-weight: 500; color: #6b7280;">Date & Time:</span>
                            <span style="font-weight: 600; color: #1f2937;">{timestamp}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 12px 0;">
                            <span style="font-weight: 500; color: #6b7280;">Status:</span>
                            <span style="background: #dcfce7; color: #166534; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 14px;">Completed</span>
                        </div>
                    </div>
                </div>
                
                <!-- What's Next Section -->
                <div style="background: #f9fafb; border-radius: 12px; padding: 24px; margin-bottom: 32px;">
                    <h3 style="margin: 0 0 16px; font-size: 18px; color: #1f2937; font-weight: 600;">
                        What you can do now:
                    </h3>
                    <div style="color: #4b5563; line-height: 1.6;">
                        <p style="margin: 0 0 8px;">• Browse available tasks in your area</p>
                        <p style="margin: 0 0 8px;">• Post your own tasks and hire professionals</p>
                        <p style="margin: 0 0 8px;">• Make secure payments for completed work</p>
                        <p style="margin: 0;">• Track your wallet balance anytime</p>
                    </div>
                </div>
                
                <!-- Security & Support Notice -->
                <div style="text-align: center; margin-bottom: 32px;">
                    <div style="background: #eff6ff; border: 1px solid #dbeafe; border-radius: 8px; padding: 20px;">
                        <p style="margin: 0; font-size: 14px; color: #1e40af; line-height: 1.5; font-weight: 500;">
                            Questions about this transaction?<br>
                            Contact our support team anytime for assistance.
                        </p>
                    </div>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background: #f9fafb; padding: 32px 40px; border-top: 1px solid #f0f0f0;">
                <div style="text-align: center;">
                    <img src="{favicon_logo}" alt="duotasks" style="height: 100px; width: auto; margin-bottom: 16px; opacity: 0.7;">
                    <p style="margin: 0 0 8px; font-size: 16px; color: #1f2937; font-weight: 600;">
                        duotasks
                    </p>
                    <p style="margin: 0 0 16px; font-size: 14px; color: #6b7280;">
                        Your trusted community platform
                    </p>
                    <div style="margin-bottom: 16px;">
                        <a href="https://duotasks.net" style="color: #00915a; text-decoration: none; font-size: 14px; margin: 0 12px;">
                            Visit Website
                        </a>
                        <a href="mailto:support@duotasks.net" style="color: #00915a; text-decoration: none; font-size: 14px; margin: 0 12px;">
                            Contact Support
                        </a>
                    </div>
                    <div style="border-top: 1px solid #e5e7eb; padding-top: 16px;">
                        <p style="margin: 0; font-size: 12px; color: #9ca3af;">
                            © 2025 duotasks. All rights reserved.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </body>
    """

from .helpers import first_name

full_logo = "https://res.cloudinary.com/dfvauxrrg/image/upload/v1763130303/full_scpz7t.png"
favicon_logo = "https://res.cloudinary.com/dfvauxrrg/image/upload/v1763130303/logo_pjlj60.png"

def wallet_authorization_email_template(name, amount, task_name, task_id, worker_name, worker_phone, worker_profile_image, timestamp):
    name = first_name(name)
    worker_first_name = first_name(worker_name)
    return f"""
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; color: #1a1a1a; padding: 20px; margin: 0; min-height: 100vh;">
        <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); overflow: hidden;">
            
            <!-- Header -->
            <div style="background: #ffffff; padding: 32px 40px 24px; text-align: center; border-bottom: 1px solid #f0f0f0;">
                <img src="{full_logo}" alt="duotasks" style="height: 150px; width: auto; margin-bottom: 8px;">
            </div>
            
            <!-- Main Content -->
            <div style="padding: 48px 40px;">
                <!-- Authorization Notice Section -->
                <div style="text-align: center; margin-bottom: 40px;">
                    <div style="background: #fbbf24; width: 80px; height: 80px; border-radius: 50%; margin: 0 auto 24px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 16px rgba(251, 191, 36, 0.25);">
                        <span style="color: white; font-size: 40px;">🔒</span>
                    </div>
                    <h1 style="margin: 0 0 16px; font-size: 28px; font-weight: 600; color: #1a1a1a; line-height: 1.3;">
                        Payment Authorized
                    </h1>
                    <p style="margin: 0; font-size: 18px; color: #6b7280; line-height: 1.5;">
                        Hi {name}, funds have been reserved for your task
                    </p>
                </div>
                
                <!-- Amount Section -->
                <div style="background: #fffbeb; border: 2px solid #fde68a; border-radius: 16px; padding: 32px; text-align: center; margin-bottom: 32px;">
                    <p style="margin: 0 0 16px; font-size: 16px; color: #92400e; font-weight: 500;">
                        Amount Authorized
                    </p>
                    <div style="background: #f59e0b; color: white; padding: 20px 32px; border-radius: 12px; display: inline-block; box-shadow: 0 4px 16px rgba(245, 158, 11, 0.25);">
                        <span style="font-size: 36px; font-weight: 700; font-family: 'Courier New', monospace;">
                            KES {amount:,.2f}
                        </span>
                    </div>
                    <div style="margin-top: 24px; padding: 16px; background: #dbeafe; border-radius: 8px; border-left: 4px solid #3b82f6;">
                        <p style="margin: 0; font-size: 14px; color: #1e40af; font-weight: 500;">
                            This amount is held securely until task completion
                        </p>
                    </div>
                </div>
                
                <!-- Task Details Section -->
                <div style="background: #f9fafb; border-radius: 12px; padding: 24px; margin-bottom: 32px;">
                    <h3 style="margin: 0 0 20px; font-size: 18px; color: #1f2937; font-weight: 600;">
                        Task Details
                    </h3>
                    <div style="color: #4b5563; line-height: 1.8;">
                        <div style="padding: 12px 0; border-bottom: 1px solid #e5e7eb;">
                            <p style="margin: 0 0 4px; font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Task Name</p>
                            <p style="margin: 0; font-weight: 600; color: #1f2937; font-size: 16px;">{task_name}</p>
                        </div>
                        <div style="padding: 12px 0; border-bottom: 1px solid #e5e7eb;">
                            <p style="margin: 0 0 4px; font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Task ID</p>
                            <p style="margin: 0; font-weight: 600; color: #1f2937; font-family: 'Courier New', monospace;">{task_id}</p>
                        </div>
                        <div style="padding: 12px 0; border-bottom: 1px solid #e5e7eb;">
                            <p style="margin: 0 0 4px; font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Agreed Amount</p>
                            <p style="margin: 0; font-weight: 600; color: #00915a; font-size: 18px;">KES {amount:,.2f}</p>
                        </div>
                        <div style="padding: 12px 0;">
                            <p style="margin: 0 0 4px; font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Authorization Time</p>
                            <p style="margin: 0; font-weight: 600; color: #1f2937;">{timestamp}</p>
                        </div>
                    </div>
                </div>
                
                <!-- Worker Profile Section -->
                <div style="background: #f0fdfa; border: 2px solid #99f6e4; border-radius: 16px; padding: 32px; margin-bottom: 32px;">
                    <h3 style="margin: 0 0 24px; font-size: 18px; color: #1f2937; font-weight: 600; text-align: center;">
                        Your Task Worker
                    </h3>
                    
                    <!-- Worker Card -->
                    <div style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                        <div style="display: flex; align-items: center; margin-bottom: 20px;">
                            <img src="{worker_profile_image}" alt="{worker_name}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover; border: 3px solid #00915a; margin-right: 20px;">
                            <div style="flex: 1;">
                                <h4 style="margin: 0 0 8px; font-size: 20px; color: #1f2937; font-weight: 600;">
                                    {worker_name}
                                </h4>
                                <div style="background: #dcfce7; color: #166534; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 12px; display: inline-block;">
                                    ASSIGNED
                                </div>
                            </div>
                        </div>
                        
                        <!-- Contact Info -->
                        <div style="background: #f9fafb; border-radius: 8px; padding: 16px;">
                            <div style="margin-bottom: 12px;">
                                <p style="margin: 0 0 4px; font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Contact Name</p>
                                <p style="margin: 0; font-weight: 600; color: #1f2937; font-size: 16px;">{worker_name}</p>
                            </div>
                            <div>
                                <p style="margin: 0 0 4px; font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Phone Number</p>
                                <p style="margin: 0; font-weight: 600; color: #00915a; font-size: 16px; font-family: 'Courier New', monospace;">
                                    📞 {worker_phone}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- What Happens Next Section -->
                <div style="background: #eff6ff; border-radius: 12px; padding: 24px; margin-bottom: 32px;">
                    <h3 style="margin: 0 0 16px; font-size: 18px; color: #1f2937; font-weight: 600;">
                        What happens next:
                    </h3>
                    <div style="color: #1e40af; line-height: 1.6;">
                        <p style="margin: 0 0 8px;">• {worker_first_name} will contact you to start the task</p>
                        <p style="margin: 0 0 8px;">• The authorized amount is safely held in escrow</p>
                        <p style="margin: 0 0 8px;">• Payment is released only after task completion</p>
                        <p style="margin: 0;">• You can review and confirm completion on your dashboard</p>
                    </div>
                </div>
                
                <!-- Important Notice -->
                <div style="text-align: center; margin-bottom: 32px;">
                    <div style="background: #fef3c7; border: 1px solid #fde68a; border-radius: 8px; padding: 20px;">
                        <p style="margin: 0; font-size: 14px; color: #92400e; line-height: 1.5; font-weight: 500;">
                            💡 The authorized amount remains in your wallet but is reserved for this task.<br>
                            It will be transferred to {worker_first_name} once you confirm task completion.
                        </p>
                    </div>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background: #f9fafb; padding: 32px 40px; border-top: 1px solid #f0f0f0;">
                <div style="text-align: center;">
                    <img src="{favicon_logo}" alt="duotasks" style="height: 100px; width: auto; margin-bottom: 16px; opacity: 0.7;">
                    <p style="margin: 0 0 8px; font-size: 16px; color: #1f2937; font-weight: 600;">
                        duotasks
                    </p>
                    <p style="margin: 0 0 16px; font-size: 14px; color: #6b7280;">
                        Secure payments, trusted connections
                    </p>
                    <div style="margin-bottom: 16px;">
                        <a href="https://duotasks.net" style="color: #f59e0b; text-decoration: none; font-size: 14px; margin: 0 12px;">
                            Visit Website
                        </a>
                        <a href="mailto:support@duotasks.net" style="color: #f59e0b; text-decoration: none; font-size: 14px; margin: 0 12px;">
                            Contact Support
                        </a>
                    </div>
                    <div style="border-top: 1px solid #e5e7eb; padding-top: 16px;">
                        <p style="margin: 0; font-size: 12px; color: #9ca3af;">
                            © 2025 duotasks. All rights reserved.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </body>
    """